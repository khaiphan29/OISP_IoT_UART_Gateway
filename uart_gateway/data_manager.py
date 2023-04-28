import sys, time, threading
from Adafruit_IO import MQTTClient
from functools import partial

from uart_helper import *
from ai_models.AI_GGTM import *
from ai_models.AI_Yolov5s import *
from webcam_helper import *
from adafruit_keys import AIO_USERNAME, AIO_KEY

#1-Hop
RETRY_TIME_OUT = 3
MAX_RETRIES = 3

#UART Signal message for LED and Fan
UART_LIGHT_ON = "L1"
UART_LIGHT_OFF = "L0"
UART_FAN_ON = "F1"
UART_FAN_OFF = "F0"
UART_READ_DATA_FREQUENCY = "T"

#Adafruit active state
AIO_ACTIVE_STATE = "1"
AIO_INACTIVE_STATE = "0"

AIO_STATUS = {"1": "STARTUP", "2": "OPERATION"}


#FEED ID to subscribe
AIO_FEED_ID = ["nutnhan1", "nutnhan2", "nutnhan3", "datafrequency"]
AIO_DATA_FREQUENCY_FEED = "datafrequency"
AIO_AUTOMATION_FEED = "nutnhan3"

#The destination where the data is publish
PUBLISH_DATA_FEED_DESTINATION = {"TEMP": "cambien1", "HUMID": "cambien2", "BRIGHT": "cambien3", "STATUS": "sensorstatus"}
PUBLISH_DATA_FEED_RANGE = {"TEMP": [-100,100], "HUMID": [0,100], "BRIGHT": [0,100], "STATUS": [0,2]}
UART_STATUS_TYPE = "STATUS"

GOOGLE_TM_FEED = "ai"
TWO_HOP_FEED = "twohop"

#The state of uart modules
AIO_UART_STATE = {
    'nutnhan1': {
        AIO_ACTIVE_STATE: UART_LIGHT_ON,
        AIO_INACTIVE_STATE: UART_LIGHT_OFF
    },
    'nutnhan2': {
        AIO_ACTIVE_STATE: UART_FAN_ON,
        AIO_INACTIVE_STATE: UART_FAN_OFF
    }
}

#DETECT HUMAN YOLO
YOLO_HUMAN_OBJECT = 'person'

#TIME_INTERVAL for sensor data pusblishing scheduler
DEFAULT_SENSOR_DATA_PUBLSIHING_TIME_INTERVAL = 30
AI_DATA_PUBLSIHING_TIME_INTERVAL = 10

#SLEEPING TIME in second(s)
SLEEPING_TIME = 1

class DataManager:
    def __init__(self) -> None:
        #Initialize Helpers
        self.my_uart = UARTHelper()
        self.my_webcam = WebcamHelper()
        self.my_yolo = YoloHelper()
        self.my_ggtm = GGTeachableMachineHelper()
        self.automation_stop_event = threading.Event()

        self.one_hop_stop_event = {}
        for feed in AIO_FEED_ID:
            if feed != "datafrequency":
                self.one_hop_stop_event[feed] = threading.Event()

        #Initialize MQTT Client
        self.client = MQTTClient(AIO_USERNAME , AIO_KEY)
        self.establishConnection()

    def establishConnection(self):
        #set callback
        self.client.on_connect = self.__connected
        self.client.on_disconnect = self.__disconnected
        self.client.on_message = self.__message
        self.client.on_subscribe = self.__subscribe
        self.client.connect()
        #loop_foreground se ko cho hien thuc them (locking)
        self.client.loop_background()

    #Set up MQTT callback
    def __connected(self, client):
        for topic in AIO_FEED_ID:
            self.client.subscribe(topic)
        self.client.subscribe(TWO_HOP_FEED)
        time.sleep(1)
        self.client.receive(AIO_DATA_FREQUENCY_FEED)

    def __subscribe(self, client , userdata , mid , granted_qos):
        print("Subscribed successfully.")

    def __disconnected(self, client):
        sys.exit (1)

    def __message(self, client , feed_id , payload):
        print("Get: " + payload + " from Feed: " + feed_id)
        if feed_id == TWO_HOP_FEED:
            stop_feed_id = self.get_feed_id_two_hop_msg(payload)
            self.one_hop_stop_event[stop_feed_id].set()
            return

        elif feed_id == AIO_DATA_FREQUENCY_FEED:
            self.my_uart.writeData(UART_READ_DATA_FREQUENCY + payload)
            self.sensor_data_publishing_interval = int(payload)
            return
        
        elif feed_id == AIO_AUTOMATION_FEED:
            if payload == AIO_ACTIVE_STATE:
                self.automation_stop_event.clear()
                threading.Thread(target=self.automation, args=(self.automation_stop_event,)).start()
            elif payload == AIO_INACTIVE_STATE:
                self.automation_stop_event.set()
            
            #response to server
            msg = self.two_hop_msg(feed_id, payload)
            threading.Thread(target=self.one_hop_publishing, args=(TWO_HOP_FEED, msg, self.one_hop_stop_event[feed_id])).start()
            return
        
        #Update state to modules
        self.my_uart.writeData(AIO_UART_STATE[feed_id][payload])
        msg = self.two_hop_msg(feed_id, payload)
        threading.Thread(target=self.one_hop_publishing, args=(TWO_HOP_FEED, msg, self.one_hop_stop_event[feed_id])).start()

    def two_hop_msg (self, feed_id, payload) -> str:
        return "!GW:" + str(feed_id) + ":" + str(payload) + "#"
    
    def get_feed_id_two_hop_msg(self, data: str):
        data = data.replace("!", "")
        data = data.replace("#", "")
        data = data.split(":")
        return data[1]

    def one_hop_publishing(self, feed, payload, stop_event: threading.Event):
        retries = 0
        counter = 0
        self.client.publish(feed, payload)
        stop_event.clear()
        while not stop_event.is_set():
            counter += 1
            if retries >= MAX_RETRIES:
                break
            if counter >= RETRY_TIME_OUT:
                counter = 0
                retries += 1
                self.client.publish(feed, payload)

            time.sleep(1)
        
        if not stop_event.is_set():
            print ("Failed: publish " + str(payload) + " to feed " + str(feed))
            return

        print ("Successfully: publish " + str(payload) + " to feed " + str(feed))

    def updateUartMsg(self):
        for data in self.my_uart.readSerial():
            if float(data.value) >= PUBLISH_DATA_FEED_RANGE[data.type][0] and float(data.value) <= PUBLISH_DATA_FEED_RANGE[data.type][1]:
                if data.type == UART_STATUS_TYPE:
                    self.client.publish(PUBLISH_DATA_FEED_DESTINATION[data.type], AIO_STATUS[data.value])
                else:
                    self.client.publish(PUBLISH_DATA_FEED_DESTINATION[data.type], data.value)
            else:
                print (data.type + ": " + data.value + " is out of range (" + str(PUBLISH_DATA_FEED_RANGE[data.type][0]) + "," + str(PUBLISH_DATA_FEED_RANGE[data.type][1] + 1) + ")")

    def updateAIData(self):
        image = self.my_webcam.get_webcam_image()

        #Publish data from GGTM
        self.client.publish(GOOGLE_TM_FEED, self.my_ggtm.image_detector(image))

    def run(self):
        self.sensor_data_publishing_interval = DEFAULT_SENSOR_DATA_PUBLSIHING_TIME_INTERVAL
        counter = 0
        ai_counter = AI_DATA_PUBLSIHING_TIME_INTERVAL
        try:
            while True:
                #Publishing Sensors Data
                counter += SLEEPING_TIME
                if counter >= self.sensor_data_publishing_interval:
                    print ("Try publishing sensor data...")
                    counter = 0
                    self.updateUartMsg()

                #Publishing AI result
                ai_counter -= SLEEPING_TIME
                if ai_counter <= 0:
                    print ("Try publishing AI data...")
                    ai_counter = AI_DATA_PUBLSIHING_TIME_INTERVAL
                    self.updateAIData()

                time.sleep (SLEEPING_TIME)

        #disconnect when we type ^C
        except KeyboardInterrupt:
            self.mqttDisconnect()

    def automation(self, stop_event):
        #turn the modules off
        self.my_uart.writeData(AIO_UART_STATE["nutnhan1"][AIO_INACTIVE_STATE])
        time.sleep (SLEEPING_TIME)
        self.my_uart.writeData(AIO_UART_STATE["nutnhan2"][AIO_INACTIVE_STATE]) 

        state = AIO_INACTIVE_STATE
        while not stop_event.is_set():

            #get AI detection result
            image = self.my_webcam.get_webcam_image()
            yolo_is_human = YOLO_HUMAN_OBJECT in self.my_yolo.yolo_detected_object(image)
            print("Yolo Detected Human: " + str(yolo_is_human))

            #change state of module whenever the detection result changes
            if yolo_is_human and state == AIO_INACTIVE_STATE:
                state = AIO_ACTIVE_STATE
                self.my_uart.writeData(AIO_UART_STATE["nutnhan1"][AIO_ACTIVE_STATE])
                time.sleep (SLEEPING_TIME)
                self.my_uart.writeData(AIO_UART_STATE["nutnhan2"][AIO_ACTIVE_STATE])
            elif not yolo_is_human and state == AIO_ACTIVE_STATE:
                state = AIO_INACTIVE_STATE
                self.my_uart.writeData(AIO_UART_STATE["nutnhan1"][AIO_INACTIVE_STATE])
                time.sleep (SLEEPING_TIME)
                self.my_uart.writeData(AIO_UART_STATE["nutnhan2"][AIO_INACTIVE_STATE]) 

            time.sleep (SLEEPING_TIME)

        #turn the modules off
        self.my_uart.writeData(AIO_UART_STATE["nutnhan1"][AIO_INACTIVE_STATE])
        time.sleep (SLEEPING_TIME)
        self.my_uart.writeData(AIO_UART_STATE["nutnhan2"][AIO_INACTIVE_STATE]) 

    def mqttDisconnect(self):
        self.client.disconnect()
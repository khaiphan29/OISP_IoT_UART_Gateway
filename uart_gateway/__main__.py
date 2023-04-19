import sys, time, random
from Adafruit_IO import MQTTClient

from uart_helper import *
from ai_models.AI_GGTM import *
from ai_models.AI_Yolov5s import *
from webcam_helper import *
from adafruit_keys import AIO_USERNAME, AIO_KEY

#UART Signal message for LED and Fan
UART_LIGHT_ON = "L1"
UART_LIGHT_OFF = "L0"
UART_FAN_ON = "F1"
UART_FAN_OFF = "F0"

#Adafruit active state
AIO_ACTIVE_STATE = "1"
AIO_INACTIVE_STATE = "0"

#FEED ID to subscribe
AIO_FEED_ID = ["nutnhan1", "nutnhan2"]

#The destination where the data is publish
DATA_FEED_DESTINATION = {"TEMP": "cambien1", "HUMID": "cambien2", "BRIGHT": "cambien3"}
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
GOOGLE_TM_FEED = "ai"
YOLO_FEED = "yoloai"

#TIME_INTERVAL for sensor data pusblishing scheduler
SENSOR_DATA_PUBLSIHING_TIME_INTERVAL = 30
AI_DATA_PUBLSIHING_TIME_INTERVAL = 10

#SLEEPING TIME in second(s)
SLEEPING_TIME = 1

#DETECT HUMAN YOLO
YOLO_HUMAN_OBJECT = 'person'

#Initialize Helpers
my_uart = UARTHelper()
my_webcam = WebcamHelper()
my_yolo = YoloHelper()
my_ggtm = GGTeachableMachineHelper()

#Set up MQTT callback
def connected(client):
    for topic in AIO_FEED_ID:
        client.subscribe(topic)

total_subscription = len(AIO_FEED_ID)
def subscribe(client , userdata , mid , granted_qos):
    print("Subscribed successfully.")
    # if total_subscription > 0:
    #     total_subscription -= 1
    # else:
    #     if my_uart.connected:
    #         start_working()

def disconnected(client):
    sys.exit (1)

def message(client , feed_id , payload):
    print("Get: " + payload + " from Feed: " + feed_id)
    my_uart.writeData(AIO_UART_STATE[feed_id][payload])

client = MQTTClient(AIO_USERNAME , AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
#loop_foreground se ko cho hien thuc them (locking)
client.loop_background()


counter = SENSOR_DATA_PUBLSIHING_TIME_INTERVAL
ai_counter = AI_DATA_PUBLSIHING_TIME_INTERVAL
try:
    while True:
        #Publishing Sensors Data
        counter -= SLEEPING_TIME
        if counter <= 0:
            print ("Try publishing sensor data...")
            counter = SENSOR_DATA_PUBLSIHING_TIME_INTERVAL
            for data in my_uart.readSerial():
                client.publish(DATA_FEED_DESTINATION[data.sensor], data.value)

        #Publishing AI result
        ai_counter -= SLEEPING_TIME
        if ai_counter <= 0:
            print ("Try publishing AI data...")
            ai_counter = AI_DATA_PUBLSIHING_TIME_INTERVAL
            image = my_webcam.get_webcam_image()

            #Publish data from GGTM
            client.publish(GOOGLE_TM_FEED, my_ggtm.image_detector(image))

            #Publish data from Yolo
            yolo_is_human = YOLO_HUMAN_OBJECT in my_yolo.yolo_detected_object(image)
            print("Yolo Detected Human: " + str(yolo_is_human))
            client.publish(YOLO_FEED, yolo_is_human)

        time.sleep (SLEEPING_TIME)

#disconnect when we type ^C
except KeyboardInterrupt:
    client.disconnect()
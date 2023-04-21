import sys, time, random
from Adafruit_IO import MQTTClient
import threading

from uart_helper import *
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
AIO_FEED_ID = ["nutnhan3"]

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
    if feed_id == "nutnhan3":
        if payload == "1":
            # start the thread
            stop_event.clear()
            thread = threading.Thread(target=automation)
            thread.start()
        else:
            # stop the loop
            stop_event.set()
        return

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

# def stop(stop_event):
#     stop_event.set()

stop_event = threading.Event()
def automation():
    state = AIO_INACTIVE_STATE
    while not stop_event.is_set():
        image = my_webcam.get_webcam_image()
        yolo_is_human = YOLO_HUMAN_OBJECT in my_yolo.yolo_detected_object(image)
        print("Yolo Detected Human: " + str(yolo_is_human))
        if yolo_is_human and state == AIO_INACTIVE_STATE:
            state = AIO_ACTIVE_STATE
            my_uart.writeData(AIO_UART_STATE["nutnhan1"][AIO_ACTIVE_STATE])
            time.sleep (SLEEPING_TIME)
            my_uart.writeData(AIO_UART_STATE["nutnhan2"][AIO_ACTIVE_STATE])
        elif not yolo_is_human and state == AIO_ACTIVE_STATE:
            state = AIO_INACTIVE_STATE
            my_uart.writeData(AIO_UART_STATE["nutnhan1"][AIO_INACTIVE_STATE])
            time.sleep (SLEEPING_TIME)
            my_uart.writeData(AIO_UART_STATE["nutnhan2"][AIO_INACTIVE_STATE])
        
        time.sleep (SLEEPING_TIME)

while True: 
    time.sleep (SLEEPING_TIME)  
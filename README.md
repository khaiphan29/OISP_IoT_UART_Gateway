# [OISP_IoT Project] UART Gateway
Our IoT project is to develop a simple IoT system for Smarthome \
 \
This is just a part of IoT project, this module acts as a gateway for interaction between Yolobit MCU and Adafruit server. \
The course's instructions is in this Youtube playlist [IoT Application Developement](https://youtube.com/playlist?list=PLyD_mbw_VznORt7CY33jGoCamjVOPyPQj). Our project is developed from those  instrucions with more features added.

## Android application
The second part of this project is a android app for end user to interact with the system. You can have a look at it on this [Github repo](https://github.com/khaiphan29/OISP_IoT_AndroidApp)

## Yolobit programming
Our MCU is AIOT KIT, which is Yolobit with extensions \
The source code of Yolobit is store in file [yolobit_ohsteam/aiot_v1.json.json](/yolobit_ohsteam/aiot_v1.json.json) \
You can import code to Yolobit MCU at [OhStem Web App](https://app.ohstem.vn/) \
For further information, you can read docs at [OhStem AIOT Docs](https://docs.ohstem.vn/en/latest/aiot/lam_quen.html)

## Installation
You should clone this project then create a virtual Python env
Install Python packages
```
pip install -r requirement.txt

#Install yolov5
git clone https://github.com/ultralytics/yolov5  # clone
cd yolov5
pip install -r requirements.txt  # install
```
## Run the gateway
```
python uart_gateway
```
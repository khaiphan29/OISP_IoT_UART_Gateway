import serial.tools.list_ports
from serial import Serial
from typing import List

class UARTSensorData:
    type: str
    value: str

    def __init__(self, type, value) -> None:
        self.type = type
        self.value = value

class UARTHelper:
    __uartPort: str
    __ser: Serial = None

    def __init__(self):
        self.mess = ""
        self.connect()

    def connect(self):
        self.__uartPort = self.__getPort()
        if self.__uartPort != "None":
            self.__ser = serial.Serial(port=self.__uartPort, baudrate=115200)
            print("Connected to UART")
            self.connected = True
            return
        self.connected = False
        print("Failed to connected to UART")

    #the getPort functions is modified so that it can work with my Mac -> get The first USE Serial port it can find.
    def __getPort(self):
        ports = serial.tools.list_ports.comports()
        N = len(ports)
        commPort = "None"
        for i in range(0, N):
            port = ports[i]
            strPort = str(port)
            #print (strPort)
            if "USB Serial" in strPort:
                splitPort = strPort.split(" ")
                commPort = (splitPort[0])
                break
        return commPort

    def __processData(self, data: str) -> UARTSensorData:
        data = data.replace("!", "")
        data = data.replace("#", "")
        splitData = data.split(":")
        #print(splitData)
        print("UART: Send data: " + splitData[0] + ": " + splitData[1])
        return UARTSensorData(splitData[0], splitData[1])
        # if splitData[0] == "TEMP":
        #     client.publish("cambien1", splitData[1])
        # elif splitData[0] == "HUMID":
        #     client.publish("cambien2", splitData[1])
        # elif splitData[0] == "BRIGHT":
        #     client.publish("cambien3", splitData[1])

    
    def readSerial(self) -> List[UARTSensorData]:
        print("READ SERIAL: ")
        try:
            bytesToRead = self.__ser.inWaiting()
            sensor_data = []
            if (bytesToRead > 0):
                self.mess = self.mess + self.__ser.read(bytesToRead).decode("UTF-8")
                while ("#" in self.mess) and ("!" in self.mess):
                    start = self.mess.find("!")
                    end = self.mess.find("#")
                    sensor_data.append(self.__processData(self.mess[start:end + 1]))
                    #update var mess
                    if (end == len(self.mess)):
                        self.mess = ""
                    else:
                        self.mess = self.mess[end+1:]
            return sensor_data
        
        except Exception as e:
            print (e)
            print("Try to reconnect to UART.")
            self.connect()
            return []
            

    def writeData(self, payload):
        try:
            print("UART: Write data: " + payload)
            self.__ser.write((str(payload)).encode())
        except Exception as e:
            print (e)
            print("Try to reconnect to UART.")
            self.connect()
            pass
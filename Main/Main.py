import sys
from sys import *
import json
from colorama import Fore  #Permet de print en couleur
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


sys.path.append(".")
from Mqtt import Mqtt
from HardwareHandler import HardwareHandler #Permet de creer un hardware et d'executer son code en //, les hardwares fonctionnelles sont stockés dans un dictionnaire
from Motor import Motor
from Lidar import Lidar
from MiniLidar import MiniLidar
from Camera import Camera
from Gyro import Gyro
from Radio import Radio
from DataBase import DataBase
from RoboticArm import RoboticArm


class Main(QMainWindow):

    def __init__(self):
        super(Main, self).__init__()
        
        with open('Main/idRobot.json') as f: #Permet de recuperer l'uinque ID associé a la carte
            self.idRobot = json.load(f)
        print(f"{Fore.GREEN}INFO (main) -> Initialising {self.idRobot}")
        listSensor = ["gyro", "miniLidar", "motor"] 
        self.dataBase = DataBase.DataBase("main")
        self.dataBase.initSensorTable(listSensor)
        # créer chaque hardware
        self.hardwareHandler = HardwareHandler.HardwareHandler()
        # 1er paramètre : nom du hardware, 2 ème paramètre class du hardware

        self.hardwareHandler.addHardware("radio", Radio.Radio)

        self.hardwareHandler.addHardware("motor", Motor.Motor)

        self.hardwareHandler.addHardware("roboticArm", RoboticArm.RoboticArm)

        #self.hardwareHandler.addHardware("camera", Camera.Camera)

        #self.hardwareHandler.addHardware("lidar", lidar.Lidar)

        self.hardwareHandler.addHardware("miniLidar", MiniLidar.MiniLidar)

        #self.hardwareHandler.addHardware("gyro", Gyro.Compass)

        self.hardwareHandler.runThreadHardware()
        
        self.gyro = Gyro.Compass()

        #self.miniLidar = MiniLidar.MiniLidar()

        self.lidar = Lidar.Lidar()

        layout = QVBoxLayout()
	
        self.runMotorButton = QPushButton("Run Motor")
        self.runMotorButton.pressed.connect(self.runMotor)    

        self.stopMotorButton = QPushButton("Stop Motor")
        self.stopMotorButton.pressed.connect(self.stopMotor) 

        self.cameraButton = QPushButton("Camera")
        self.cameraButton.pressed.connect(self.photoCamera)   

        self.radioSendButton = QPushButton("Radio send")
        self.radioSendButton.pressed.connect(self.sendRadio) 

        self.closeCodeButton = QPushButton("Close Code")
        self.closeCodeButton.pressed.connect(self.closeEvent) 

        self.runLidarButton = QPushButton("Run Lidar")
        self.runLidarButton.pressed.connect(self.runLidar) 

        self.robotNumberInput = QLabel()
        self.robotNumberInput.setText("Robot number ?")
        self.robotNumber = QLineEdit("1")

        self.speedInput = QLabel()
        self.speedInput.setText('Motor speed:')
        self.motorSpeed = QLineEdit("50")

        self.timeInput = QLabel()
        self.timeInput.setText('Motor time:')
        self.motorTime = QLineEdit("3")

        self.directionInput = QLabel()
        self.directionInput.setText('Motor direction:')
        self.motorDirection = QLineEdit("1")
        
        self.radioInput = QLabel()
        self.radioInput.setText('Radio payload')
        self.radioPayload = QLineEdit("send/motor_command/3-1-0-30-0")

        self.roboticArmInput = QLabel()
        self.roboticArmInput.setText('Robotic Arm payload')
        self.roboticArmPayload = QLineEdit("20-200-150-0-80-40")

        self.gyroValue = QLabel()
        self.gyroValue.setText('Gyro value:')

        self.miniLidarValue = QLabel()
        self.miniLidarValue.setText('Mini lidar value:')

        self.roboticArmRun = QPushButton("Move robotic arm")
        self.roboticArmRun.pressed.connect(self.runRoboticArm) 

        layout.addWidget(self.robotNumberInput)
        layout.addWidget(self.robotNumber)
        layout.addWidget(self.runMotorButton)
        layout.addWidget(self.speedInput)
        layout.addWidget(self.motorSpeed)
        layout.addWidget(self.directionInput)
        layout.addWidget(self.motorDirection)
        layout.addWidget(self.timeInput)
        layout.addWidget(self.motorTime)

        layout.addWidget(self.stopMotorButton)
        layout.addWidget(self.closeCodeButton)
        
        layout.addWidget(self.radioSendButton)
        layout.addWidget(self.radioInput)
        layout.addWidget(self.radioPayload)
        
        layout.addWidget(self.runLidarButton)

        layout.addWidget(self.roboticArmRun)
        layout.addWidget(self.roboticArmInput)
        layout.addWidget(self.roboticArmPayload)
        
        layout.addWidget(self.gyroValue)
        layout.addWidget(self.miniLidarValue)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()

        self.listChannel = ["all"]
        self.mqtt = Mqtt.Mqtt(hardwareName="main", on_message=self.on_message, listChannel=self.listChannel)

        timer = QTimer(self)
        timer.setInterval(500)
        timer.timeout.connect(self.updateBoard)
        timer.start()
        

    def updateBoard(self):
        
        gyroValue = str(self.gyro.getSensorValue()).split("-")
        compass = gyroValue[0]
        picth = gyroValue[1]
        roll = gyroValue[2]

        # miniLidarValue = str(round(self.miniLidar.getSensorValue()))

        motorValue = self.dataBase.getSensorValue("motor").split("-")
        motorSpeed = str(motorValue[3])
        motorDirection = str(motorValue[1])
        motorTime = str(motorValue[0])

        self.gyroValue.setText(f"Gyro value : \n\tCompass: {compass} Pitch: {picth} Roll: {roll} ")
        # self.miniLidarValue.setText(f"MiniLidar value : \n\t Distance : {miniLidarValue}")
        self.motorSpeed.setPlaceholderText(motorSpeed)
        self.motorDirection.setPlaceholderText(motorDirection)
        self.motorTime.setPlaceholderText(motorTime)

    def runLidar(self):
        self.mqtt.sendMessage(message="command/scan", receiver="lidar")

    def closeEvent(self):
        app.quit()
        100/0

    def sendRadio(self):
        self.mqtt.sendMessage(message="send/bonjour", receiver="radio", awnserNeeded=False)

    def on_message(self, client, data, message):
        self.mqtt.decodeMessage(message=message)

        if self.mqtt.lastCommand == "state":
            #print("State,", self.mqtt.lastSender, "is", self.mqtt.lastPayload)
            if self.mqtt.lastSender == "miniLidar":
                self.miniLidarValue.setText(f"MiniLidar value : \n\t Distance : {round(float(self.mqtt.lastPayload))}")
        
    def runMotor(self):
        payload = str(self.motorTime.text()) + "-" + str(self.motorDirection.text()) + "-0-" + str(self.motorSpeed.text()) + "-0"
        self.dataBase.updateSensorValue("motor", payload)
        payload = "run-" + str(self.motorTime.text()) + "-" + str(self.motorDirection.text()) + "-0-" + str(self.motorSpeed.text()) + "-0"
        if self.witchRobot.text() == str(self.idRobot["node"]):
            self.mqtt.sendMessage(message="command/"+payload, receiver="motor")
        else:
            payload = 'motor_'+ 'command/'+  payload
            self.mqtt.sendMessage(message="send/"+payload, receiver="radio")
    
    def runRoboticArm(self):
        payload = str(self.roboticArmPayload.text())
        #self.dataBase.updateSensorValue("motor", payload)
        #payload = "run-" + str(self.motorTime.text()) + "-" + str(self.motorDirection.text()) + "-0-" + str(self.motorSpeed.text()) + "-0"
        if self.robotNumber.text() == str(self.idRobot["node"]):
            self.mqtt.sendMessage(message="command/"+payload, receiver="roboticArm")
        else:
            payload = 'roboticArm_'+ 'command/'+  payload
            self.mqtt.sendMessage(message="send/"+payload, receiver="radio")

    def stopMotor(self):
        self.mqtt.sendMessage(message="command/stop", receiver="motor")
    
    def photoCamera(self):
        self.mqtt.sendMessage(message="command/capture", receiver="camera")


if __name__ == "__main__":

    app = QApplication([])
    windows = Main()
    sys.exit(app.exec_())

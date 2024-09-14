from datetime import datetime
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import cv2
import numpy as np
from time import sleep

from codev4.socket import WebSocketServer
from codev4.myLib.BaslerCamera import camera
from codev4.myLib import Module as mod
from codev4.myLib.FindFace import find
from codev4.myLib.Control import control
from codev4.myLib.ImageProcess import Processing

# Import các hằng số từ file config
from codev4.config import *

class RunTime(WebSocketServer):
    def __init__(self):
        super().__init__()
        self.control = control(ARDUINO_PORT, ARDUINO_BAUDRATE)
        print("Wait to connect to Arduino !")
        print("....")
        print("Connected")
        self.command = None

        self.cam = camera()
        self.cam.OpenCam()
        self.image = []

        self.Angle = ROTATION_ANGLE
        self.NumFce = int(360/self.Angle)
        self.findMango = find(MANGO_DETECTION_LOWER, MANGO_DETECTION_UPPER, self.Angle)
        
        self.speedRotate = True
        self.CAPTURE = False
        self.END = True
        self.STOP = False

        self.test = [CMD_MOVE_TO_A, CMD_MOVE_TO_B]

        self.numMango = 1

        self.center = []
        self.left = []
        self.right = []
        self.TERMINATE = False

    def CaptureImage(self):
        frame_Left = self.cam.creatframe(CAMERA_PORT_LEFT)
        frame_Center = self.cam.creatframe(CAMERA_PORT_CENTER)

        self.center.append(frame_Center)
        self.left.append(frame_Left)

    def getFace(self):
        while self.cam.cameras.IsGrabbing:
            frame_Left = self.cam.creatframe(CAMERA_PORT_LEFT)
            frame = frame_Left.copy()
            frame = mod.Scale(frame, 0.3)
            
            mango, show = self.findMango.find_Mango(frame)

            if mango:
                save, stopcheck, speedRotate = self.findMango.check_Status()
                self.END = False

                if save:
                    self.CaptureImage()
                else:
                    self.CAPTURE = False
                    
                if stopcheck is False:
                    if speedRotate == 'Max':
                        self.command = CMD_QUICK_ROTATE
                    if speedRotate == 'Medium':
                        self.command = CMD_SLOW_ROTATE
                else:
                    print("ID: ", self.numMango)
                    current_date = datetime.now().strftime("%y.%m.%d")
                    folder_name = os.path.join(current_date, IMAGE_FOLDER)
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)
                    for i in range(len(self.center)):
                        cv2.imwrite(f"{folder_name}/{self.numMango}-Center_{i+1}.jpg", self.center[i])
                    for i in range(len(self.left)):
                        cv2.imwrite(f"{folder_name}/{self.numMango}-Left_{i+1}.jpg", self.left[i])
                    
                    self.numMango += 1
                    self.command = np.random.choice(self.test)
                    self.END = True
                    sleep(2) 

            if self.END is True:
                self.center = []
                self.left = []
                self.right = []
                self.command = CMD_ON_XYLANH1
                self.findMango.resetStatus()
                self.END = False

            if self.TERMINATE:
                print('Program stopped!')
                break

    def processingImage(self):
        Data = Processing(Center_Images=self.center, Scale_Center=SCALE_CENTER, 
                        Left_Images=self.left, Scale_Left=SCALE_LEFT,
                        Right_Image=self.right, Scale_Right=SCALE_RIGHT,
                        Offset=OFFSET, NumSlice_Center=NUM_SLICE_CENTER, 
                        NumSlice_Head=NUM_SLICE_HEAD, NumSlice_Tail=NUM_SLICE_TAIL,
                        Box_Center=BOX_CENTER, Box_LeftRight=BOX_LEFT_RIGHT,
                        Func_ConstArea_Center=FUNC_CONST_AREA_CENTER,
                        Func_ConstArea_Left=FUNC_CONST_AREA_LEFT, 
                        Func_ConstArea_Right=FUNC_CONST_AREA_RIGHT,
                        Tape=False, CheckTape=[0,0,0])
        Center_RS_0 = mod.stackImages([Data.Faces_Crop_Left[2],Data.Faces_Crop_Center[0],Data.Faces_Crop_Center[2]], 0)
        Center_RS_1 = mod.stackImages([Data.Face_Crop_Right,Data.Faces_Crop_Center[1],Data.Faces_Crop_Center[3]], 0)
        Center_RS = mod.stackImages([Center_RS_0, Center_RS_1], 1)
        Area = sum(Data.AllArea)
        print(Area)
        if Area > CLASSIFICATION_THRESHOLD:
            self.command = CMD_MOVE_TO_A
        else:
            self.command = CMD_MOVE_TO_B

    def sendData(self):
        while self.STOP is False:
            self.control.doJob(self.command)

    def threadPool(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.sendData)

    def start(self):
        server_thread = threading.Thread(target=self.threadPool)
        server_thread.start()
        
        websocket_thread = threading.Thread(target=self.start_server)
        websocket_thread.start()

        self.getFace()

        server_thread.join()
        websocket_thread.join()

    def stop(self):
        print("Stopping the process...")
        self.TERMINATE = True
        self.cam.CloseCam()
        print("Process stopped.")

if __name__ == "__main__":
    project = RunTime()
    project.start()
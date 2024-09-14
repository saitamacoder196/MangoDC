import asyncio
from datetime import datetime
import json
import os
import random
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
        # self.control = control(ARDUINO_PORT, ARDUINO_BAUDRATE)
        print("Wait to connect to Arduino !")
        print("....")
        print("Connected")
        self.command = None

        # self.cam = camera()
        # self.cam.OpenCam()
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

    async def getFace(self):
        while self.cam.cameras.IsGrabbing and self.running:
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

                    left_images_paths = []
                    center_images_paths = []

                    # Save images and collect the paths
                    for i in range(len(self.center)):
                        center_path = f"{folder_name}/{self.numMango}-Center_{i+1}.jpg"
                        cv2.imwrite(center_path, self.center[i])
                        center_images_paths.append(center_path)

                    for i in range(len(self.left)):
                        left_path = f"{folder_name}/{self.numMango}-Left_{i+1}.jpg"
                        cv2.imwrite(left_path, self.left[i])
                        left_images_paths.append(left_path)

                    # Create a JSON string with the image paths
                    image_paths_message = {
                        'numMango': self.numMango,
                        'center_images': center_images_paths,
                        'left_images': left_images_paths
                    }

                    # Convert the dictionary to a JSON string
                    json_message = json.dumps(image_paths_message)

                    # Send the JSON string to clients via WebSocket
                    await self.send_message(json_message)  # Use asyncio to send the message
                    await asyncio.sleep(5)
                    # Update state
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

    

    # Function to randomly pick one of the mock data items and send it through WebSocket
    async def mock_send(self):
        # Mock data for sending to WebSocket clients
        mock_data = [
            {
                "current_item": {
                    "id": "1-VL-DE",
                    "folder_path": "D://mangoes"
                },
                "prediction_images": {
                    "Left_1": "path/to/prediction_image_left_1.jpg",
                    "Left_2": "path/to/prediction_image_left_2.jpg",
                    "Left_3": "path/to/prediction_image_left_3.jpg",
                    "Left_4": "path/to/prediction_image_left_4.jpg",
                    "Center_1": "path/to/prediction_image_center_1.jpg",
                    "Center_2": "path/to/prediction_image_center_2.jpg",
                    "Center_3": "path/to/prediction_image_center_3.jpg",
                    "Center_4": "path/to/prediction_image_center_4.jpg",
                    "Right_1": "path/to/prediction_image_right_1.jpg",
                    "Right_2": "path/to/prediction_image_right_2.jpg",
                    "Right_3": "path/to/prediction_image_right_3.jpg",
                    "Right_4": "path/to/prediction_image_right_4.jpg"
                },
                "original_images": {
                    "Left_1": "path/to/original_image_left_1.jpg",
                    "Left_2": "path/to/original_image_left_2.jpg",
                    "Left_3": "path/to/original_image_left_3.jpg",
                    "Left_4": "path/to/original_image_left_4.jpg",
                    "Center_1": "path/to/original_image_center_1.jpg",
                    "Center_2": "path/to/original_image_center_2.jpg",
                    "Center_3": "path/to/original_image_center_3.jpg",
                    "Center_4": "path/to/original_image_center_4.jpg",
                    "Right_1": "path/to/original_image_right_1.jpg",
                    "Right_2": "path/to/original_image_right_2.jpg",
                    "Right_3": "path/to/original_image_right_3.jpg",
                    "Right_4": "path/to/original_image_right_4.jpg"
                },
                "conclusion": {
                    "detected_areas": [
                        {
                            "image": "xxx",
                            "position": {
                                "x": 120,
                                "y": 450
                            },
                            "area_size": 1000,
                            "disease": "Disease A"
                        },
                        {
                            "image": "xxx2",
                            "position": {
                                "x": 220,
                                "y": 550
                            },
                            "area_size": 1500,
                            "disease": "Disease B"
                        }
                    ],
                    "total_disease_area": 85375.50,
                    "total_mango_surface_area": 559946.50,
                    "disease_area_percentage": 15.25,
                    "conclusion": "Reject: Xoài bệnh abc; Accept: Không phát hiện dấu hiệu bệnh."
                }
            },
            {
                "current_item": {
                    "id": "2-VL-DE",
                    "folder_path": "D://mangoes2"
                },
                "prediction_images": {
                    "Left_1": "path/to/prediction_image_left_1_v2.jpg",
                    "Left_2": "path/to/prediction_image_left_2_v2.jpg",
                    "Left_3": "path/to/prediction_image_left_3_v2.jpg",
                    "Left_4": "path/to/prediction_image_left_4_v2.jpg",
                    "Center_1": "path/to/prediction_image_center_1_v2.jpg",
                    "Center_2": "path/to/prediction_image_center_2_v2.jpg",
                    "Center_3": "path/to/prediction_image_center_3_v2.jpg",
                    "Center_4": "path/to/prediction_image_center_4_v2.jpg",
                    "Right_1": "path/to/prediction_image_right_1_v2.jpg",
                    "Right_2": "path/to/prediction_image_right_2_v2.jpg",
                    "Right_3": "path/to/prediction_image_right_3_v2.jpg",
                    "Right_4": "path/to/prediction_image_right_4_v2.jpg"
                },
                "original_images": {
                    "Left_1": "path/to/original_image_left_1_v2.jpg",
                    "Left_2": "path/to/original_image_left_2_v2.jpg",
                    "Left_3": "path/to/original_image_left_3_v2.jpg",
                    "Left_4": "path/to/original_image_left_4_v2.jpg",
                    "Center_1": "path/to/original_image_center_1_v2.jpg",
                    "Center_2": "path/to/original_image_center_2_v2.jpg",
                    "Center_3": "path/to/original_image_center_3_v2.jpg",
                    "Center_4": "path/to/original_image_center_4_v2.jpg",
                    "Right_1": "path/to/original_image_right_1_v2.jpg",
                    "Right_2": "path/to/original_image_right_2_v2.jpg",
                    "Right_3": "path/to/original_image_right_3_v2.jpg",
                    "Right_4": "path/to/original_image_right_4_v2.jpg"
                },
                "conclusion": {
                    "detected_areas": [
                        {
                            "image": "yyy",
                            "position": {
                                "x": 320,
                                "y": 150
                            },
                            "area_size": 800,
                            "disease": "Disease C"
                        },
                        {
                            "image": "yyy2",
                            "position": {
                                "x": 420,
                                "y": 250
                            },
                            "area_size": 1200,
                            "disease": "Disease D"
                        }
                    ],
                    "total_disease_area": 76320.50,
                    "total_mango_surface_area": 659946.50,
                    "disease_area_percentage": 11.57,
                    "conclusion": "Reject: Xoài bệnh xyz; Accept: Không phát hiện dấu hiệu bệnh."
                }
            },
            {
                "current_item": {
                    "id": "3-VL-DE",
                    "folder_path": "D://mangoes3"
                },
                "prediction_images": {
                    "Left_1": "path/to/prediction_image_left_1_v3.jpg",
                    "Left_2": "path/to/prediction_image_left_2_v3.jpg",
                    "Left_3": "path/to/prediction_image_left_3_v3.jpg",
                    "Left_4": "path/to/prediction_image_left_4_v3.jpg",
                    "Center_1": "path/to/prediction_image_center_1_v3.jpg",
                    "Center_2": "path/to/prediction_image_center_2_v3.jpg",
                    "Center_3": "path/to/prediction_image_center_3_v3.jpg",
                    "Center_4": "path/to/prediction_image_center_4_v3.jpg",
                    "Right_1": "path/to/prediction_image_right_1_v3.jpg",
                    "Right_2": "path/to/prediction_image_right_2_v3.jpg",
                    "Right_3": "path/to/prediction_image_right_3_v3.jpg",
                    "Right_4": "path/to/prediction_image_right_4_v3.jpg"
                },
                "original_images": {
                    "Left_1": "path/to/original_image_left_1_v3.jpg",
                    "Left_2": "path/to/original_image_left_2_v3.jpg",
                    "Left_3": "path/to/original_image_left_3_v3.jpg",
                    "Left_4": "path/to/original_image_left_4_v3.jpg",
                    "Center_1": "path/to/original_image_center_1_v3.jpg",
                    "Center_2": "path/to/original_image_center_2_v3.jpg",
                    "Center_3": "path/to/original_image_center_3_v3.jpg",
                    "Center_4": "path/to/original_image_center_4_v3.jpg",
                    "Right_1": "path/to/original_image_right_1_v3.jpg",
                    "Right_2": "path/to/original_image_right_2_v3.jpg",
                    "Right_3": "path/to/original_image_right_3_v3.jpg",
                    "Right_4": "path/to/original_image_right_4_v3.jpg"
                },
                "conclusion": {
                    "detected_areas": [
                        {
                            "image": "zzz",
                            "position": {
                                "x": 420,
                                "y": 320
                            },
                            "area_size": 1200,
                            "disease": "Disease E"
                        },
                        {
                            "image": "zzz2",
                            "position": {
                                "x": 520,
                                "y": 420
                            },
                            "area_size": 1800,
                            "disease": "Disease F"
                        }
                    ],
                    "total_disease_area": 98275.00,
                    "total_mango_surface_area": 859946.50,
                    "disease_area_percentage": 11.43,
                    "conclusion": "Reject: Xoài bệnh def; Accept: Không phát hiện dấu hiệu bệnh."
                }
            }
        ]
        while self.running:
            # Select a random item from the mock data
            selected_data = random.choice(mock_data)
            
            # Convert the selected item to JSON string
            message = json.dumps(selected_data)
            
            # Send the message to the WebSocket clients
            await self.send_message(message)
            
            # Wait 5 seconds before sending the next message
            await asyncio.sleep(5)

             
    def start(self):
        server_thread = threading.Thread(target=self.threadPool)
        server_thread.start()
        self.add_task(self.mock_send)
        websocket_thread = threading.Thread(target=self.start_server)
        websocket_thread.start()

        # self.getFace()

        server_thread.join()
        websocket_thread.join()

    def stop(self):
        print("Stopping the process...")
        self.TERMINATE = True
        # self.cam.CloseCam()
        print("Process stopped.")

if __name__ == "__main__":
    project = RunTime()
    project.start()
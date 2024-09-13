from datetime import datetime
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import cv2

from codev4.myLib.BaslerCamera import camera
from codev4.myLib import Module as mod
from codev4.myLib.FindFace import find
from codev4.myLib.Control import control

from numpy import random
from time import sleep

from codev4.myLib.ImageProcess import Processing

class RunTime:
    def __init__(self):
        self.control = control('COM3', 115200)
        print("Wait to connect to Arduino !")
        print("....")
        # self.control.recv_data()
        print("Connected")
        self.command = None

        self.cam = camera()
        self.cam.OpenCam()
        self.image = []

        '''Góc xoay: 10, 12, 15, 18, 20, 30, 36, 45, 60, 90'''
        self.Angle = 90 #góc xoay khi chụp ảnh
        self.NumFce = int(360/self.Angle) #Số thứ tự mặt xoài
        self.findMango = find([0, 0, 150], [255, 255, 255], self.Angle)
        
        self.speedRotate = True
        self.CAPTURE = False
        self.END = True
        self.STOP = False

        "To Classify Mango"
        self.test = ["move2A", "move2B"]

        self.numMango = 1 #Số thứ tự trái xoài

        self.center = []
        self.left = []
        self.right = []
        self.TERMINATE = False

    def CaptureImage(self):
        "Ethernet"
        frame_Left = self.cam.creatframe(1)
        "USB"
        frame_Center = self.cam.creatframe(0)
        #frame_Right = self.cam.creatframe(0)

        self.center.append(frame_Center)
        self.left.append(frame_Left) 
        #self.right.append(frame_Right)
        # cv2.imshow("Left", mod.Scale(frame_Left, 0.3))
        # cv2.imshow("Center", mod.Scale(frame_Center, 0.3))

    def getFace(self):
        while self.cam.cameras.IsGrabbing:
            frame_Left = self.cam.creatframe(1)
            #frame_Center = self.cam.creatframe(0)
            #frame_Right = self.cam.creatframe(0)
            
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
                        self.command = "quickrotate"
                    if speedRotate == 'Medium':
                        self.command = "slowrotate"
                    # if speedRotate == 'Stop':
                    #     self.command = "onxylanh3"
                else:
                    print("ID: ", self.numMango)
                    '''Bỏ command khi cần lưu ảnh'''
                    current_date = datetime.now().strftime("%y.%m.%d")
                    folder_name = os.path.join(current_date,"No Tape")
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)
                    for i in range(len(self.center)):
                        cv2.imwrite(f"{folder_name}/{self.numMango}-Center_{i+1}.jpg", self.center[i])
                    for i in range(len(self.left)):
                        cv2.imwrite(f"{folder_name}/{self.numMango}-Left_{i+1}.jpg", self.left[i])
                    # for i in range((len(self.right))):
                    #     cv2.imwrite(f"24.1.17/No Tape/{self.numMango}-Right_{i+1}.jpg", self.right[i])
                    self.numMango+=1
                    self.command = self.test[random.randint(2)] #Cho ngãu nhiên kết quả phân loại khi không tính diện tích khuyết điểm
                    '''Bỏ command khi cần thực hiện xử lý ảnh trực tiếp'''
                    # self.processingImage()
                    self.END = True
                    sleep(2) 

            if self.END is True:
                self.center = []
                self.left = []
                self.right = []
                self.command = "onxylanh1"
                self.findMango.resetStatus()
                self.END = False

            if self.TERMINATE:
                print('Program stopped!')
                break

            # cv2.imshow('Find Mango Window', show)
            # key = cv2.waitKey(1)

            # if key == ord('q'):
            #     self.STOP = True
            #     print("Stop acquiring camera")
            #     cv2.destroyAllWindows()
                # break
    
    def processingImage(self):
        Data = Processing(Center_Images=self.center, Scale_Center=0.5*0.56, 
                        Left_Images=self.left, Scale_Left=0.5*0.69,
                        Right_Image=self.right, Scale_Right=0.5,
                        Offset=10,NumSlice_Center=12, NumSlice_Head=12, NumSlice_Tail=17,
                        Box_Center=[21,15], Box_LeftRight=[13,11],
                        Func_ConstArea_Center=[6.988941860465115e-06 , 0.007519668639534884],
                        Func_ConstArea_Left=[1.9089044265593567e-05 , -0.0028447316680080513], 
                        Func_ConstArea_Right=[-1.996435199999999e-05 , 0.058740052719999984],
                        Tape = False, CheckTape=[0,0,0])
        Center_RS_0 = mod.stackImages([Data.Faces_Crop_Left[2],Data.Faces_Crop_Center[0],Data.Faces_Crop_Center[2]], 0)
        Center_RS_1 = mod.stackImages([Data.Face_Crop_Right,Data.Faces_Crop_Center[1],Data.Faces_Crop_Center[3]], 0)
        Center_RS = mod.stackImages([Center_RS_0, Center_RS_1], 1)
        # cv2.imshow("RS", Center_RS)
        Area = sum(Data.AllArea)
        print(Area)
        if Area>200:
            self.command = "move2A"
        else:
            self.command = "move2B"

    def sendData(self):
        while self.STOP is False:
            self.control.doJob(self.command)

    def threadPool(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.sendData)

    def run(self):
        thread = threading.Thread(target=self.threadPool)
        thread.start()
        self.getFace()
        thread.join()

    def stop(self):
        print("Stopping the process...")
        self.TERMINATE = True  # Đặt cờ TERMINATE thành True để dừng quá trình
        
    def terminate(self):
        """Hàm để gọi khi cần dừng tất cả các tiến trình"""
        self.TERMINATE = True
        self.cam.CloseCam()  # Đóng camera khi dừng chương trình
        print("Process terminated.")
'''Đoạn chương trình gọi hàm'''
if __name__ == "__main__":
    project = RunTime()
    project.run()




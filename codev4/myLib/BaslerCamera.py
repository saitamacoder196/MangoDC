# import os, sys
from pypylon import pylon
import cv2
import numpy as np


class camera():
    def __init__(self):
        self.frame = None
        self.tl_factory = pylon.TlFactory.GetInstance()

        self.devices = self.tl_factory.EnumerateDevices()

        self.cameras = pylon.InstantCameraArray(min(len(self.devices), 3))

        for idx, _cam_ in enumerate(self.cameras):
            _cam_.Attach(self.tl_factory.CreateDevice(self.devices[idx]))
            _cam_.Open()
            # cam.PixelFormat = "Mono8"
            _cam_.Width = _cam_.Width.Max
            _cam_.Height = _cam_.Height.Max
            # pylon.FeaturePersistence.Load(nodeFile[idx], cam[idx].GetNodeMap(), True)
            print("Using device", _cam_.GetDeviceInfo().GetModelName())

        # Chuyển đổi hệ màu sang RGB (Opencv)
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    def OpenCam(self):
        # Mở camera
        # self.cam_array.Open()
        # pylon.FeaturePersistence.Load(self.nodeFile1, self.cameras.GetNodeMap(), True)
        self.cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    def creatframe(self, Numcam):
        grab = self.cameras[Numcam].RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if grab.GrabSucceeded():
            # self.cameraContextValue = grab.GetCameraContext()
            self.frame = self.converter.Convert(grab)
            self.frame = self.frame.GetArray()
            # self.frame = self.undistortImg(self.frame)
        return self.frame

    def light_check(self,image):

        import matplotlib.pyplot as plt
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        x = np.arange(0, w)
        y = np.arange(0, h)

        x_axis, y_axis = np.meshgrid(x, y) 

        
        # Creating figure
        fig = plt.figure(figsize =(14, 9))
        ax = plt.axes(projection ='3d')
    
        # Creating color map
        my_cmap = plt.get_cmap('plasma')
        
        # Creating plot
        surf = ax.plot_surface(y_axis,x_axis, gray, cmap = my_cmap, edgecolor ='none')
        
        fig.colorbar(surf, ax = ax, shrink = 0.5, aspect = 5)
        
        ax.set_title('Surface plot')

        plt.show()


if __name__ == "__main__":

    import Module as md

    TypeCam = "/Right"  # Ten thu muc chua anh cua tung camera
    Raw = "E:/CODE/Calib/Raw"+TypeCam
    Raw_folder = "E:/CODE/Calib/Raw"

    cam = camera()
    cam.OpenCam()
    
    start_point_Center = (297, 580)
    end_point_Center = (2175, 1460)
    start_point_Left = (800, 520)
    end_point_Left = (1150, 758)
    start_point_Right = (500, 500)
    end_point_Right = (1080, 800)

    num_Light_Cent = 0
    num_Light_Right = 6
    num_Light_Left = 6 

    while cam.cameras.IsGrabbing:

        frame = cam.creatframe(0)
        # cv2.rectangle(frame, start_point_Left, end_point_Left, (255, 0, 0), 3)
        frame = md.Scale(frame, 0.4)

        h, w = frame.shape[:2]
        cen_h = h / 2
        cen_w = w / 2
        cv2.line(frame, (0, int(cen_h)), (w, int(cen_h)), (0, 0, 255), 1)
        cv2.line(frame, (int(cen_w), 0), (int(cen_w), h), (0, 0, 255), 1)
        cv2.imshow('Left Cam', frame)
        
        frame1 = cam.creatframe(1)
        # cv2.rectangle(frame1, start_point_Center, end_point_Center, (255,0, 0), 3)
        frame1 = md.Scale(frame1, 0.3)
        frame_gray = frame1[:,:,1]
        h1, w1 = frame1.shape[:2]
        cen_h1 = h1/2
        cen_w1 = w1/2
        cv2.line(frame1, (0,int(cen_h1)), (w1,int(cen_h1)), (0,0,255), 1)
        cv2.line(frame1, (int(cen_w1), 0), (int(cen_w1), h1), (0,0,255), 1)
        cv2.imshow('Center Cam', frame1)

        frame2 = cam.creatframe(2)
        # cv2.rectangle(frame2, start_point_Right, end_point_Right, (255,0, 0), 3)
        frame2 = md.Scale(frame2, 0.4)
        h2, w2 = frame2.shape[:2]
        cen_h2 = h2/2
        cen_w2 = w2/2
        cv2.line(frame2, (0,int(cen_h2)), (w1,int(cen_h2)), (0,0,255), 1)
        cv2.line(frame2, (int(cen_w2), 0), (int(cen_w2), h2), (0,0,255), 1)
        cv2.imshow('Right Cam', frame2)

        key = cv2.waitKey(1)
        # Thoát bằng nút 'q'
        if key == ord('q'):
            print("Stop acquiring camera")
            cv2.destroyAllWindows()
            break

        if key == ord('a'):
            if TypeCam == "/Center":
                frame = cam.creatframe(1)
                name = input("type picture name: ")
                print("Captured image from center camera")
                cv2.imwrite(Raw + "/" + name + ".png", frame)

            if TypeCam=="/Left":
                frame = cam.creatframe(0)
                name = input("type picture name: ")
                print("Captured image from left camera")
                cv2.imwrite(Raw + "/" + name +".png", frame)

            if TypeCam=="/Right":
                frame = cam.creatframe(2)
                name = input("type picture name: ")
                print("Captured image from right camera")
                cv2.imwrite(Raw + "/" + name +".png", frame)
        
        if key == ord('s'):
            frameC = cam.creatframe(1)
            frameL = cam.creatframe(0)
            frameR = cam.creatframe(2)
            name = input("type picture name: ")
            print("Captured image")
            cv2.imwrite(Raw_folder + "/" + name + "_Center"+".png", frameC)
            cv2.imwrite(Raw_folder + "/" + name + "_Left"  +".png", frameL)
            cv2.imwrite(Raw_folder + "/" + name + "_Right" +".png", frameR)

        if key == ord('d'):
            name = input("type picture name: ")
            print("Captured image")
            cv2.imwrite(Raw_folder + "/" + name + "_Center" +".png", frame)
            cv2.imwrite(Raw_folder + "/" + name + "_Left" +".png", frame1)
            cv2.imwrite(Raw_folder + "/" + name + "_Right" +".png", frame2)

        if key == ord('c'):
            frameC = cam.creatframe(1)
            frameC = frameC[start_point_Center[1]: end_point_Center[1], start_point_Center[0]: end_point_Center[0]]
            cam.light_check(frameC)
            cv2.imwrite(Raw_folder + "/" + "Light_Center_" + str(num_Light_Cent) + ".png", frameC)
            cv2.imwrite(Raw_folder + "/" + "Light_Center_Full_" + str(num_Light_Cent) +".png", frame1)
            num_Light_Cent+=1

        if key == ord('l'):
            frameL = cam.creatframe(0)
            frameL = frameL[start_point_Left[1]: end_point_Left[1], start_point_Left[0]: end_point_Left[0]]
            cam.light_check(frameL)
            cv2.imwrite(Raw_folder + "/" + "Light_Left_" + str(num_Light_Left) +".png", frameL)
            cv2.imwrite(Raw_folder + "/" + "Light_Left_Full_" + str(num_Light_Left) +".png", frame)
            num_Light_Left+=1

        if key == ord('r'):
            frameR = cam.creatframe(2)
            frameR = frameR[start_point_Right[1]: end_point_Right[1], start_point_Right[0]: end_point_Right[0]]
            cam.light_check(frameR)
            cv2.imwrite(Raw_folder + "/" + "Light_Right_" + str(num_Light_Right)+".png", frameR)
            cv2.imwrite(Raw_folder + "/" + "Light_Right_Full_" + str(num_Light_Right) +".png", frame2)
            num_Light_Right+=1
        



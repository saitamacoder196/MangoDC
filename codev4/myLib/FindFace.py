import cv2
import numpy as np

class find:
    """ Đầu vào lớp:
        low_green, up_green: Ngưỡng tìm ảnh nhị phân mặt đầu của camera 2
        Angle2Capture: Góc lệch của mỗi lần chụp ảnh trước và sau 
    """
    def __init__(self, low_green, up_green, Angle2Capture):
        self.low_green = low_green
        self.upp_green = up_green
        self.minArea_Mango = 1000 #Diện tích ảnh nhị phân tìm được lớn hơn giá trị này thì được xem là bề mặt xoài
        """Tọa độ vùng làm việc, tâm quả xoài nằm trong vùng này mới tiến hành xoay và chụp ảnh"""
        self.point = [187, 138] #Tọa độ điểm trên bên trái của vùng làm việc (pixel)
        self.roisize = [100, 100] #Kích thước vùng làm việc (pixel)
        """Tìm các góc xoay của quả xoài, khi xoài có giá trị gần bằng giá trị các góc xoay này, hệ thống sẽ chụp ảnh
        Ví dụ: khi góc chụp cách nhau 90 độ, thì thời điểm chụp sẽ là đầu quả xoài ở góc 90 độ, 0 độ, 90 độ và 0 độ -> [90,0,90,0]
        """
        self.setAngle2Capture = Angle2Capture
        angle = self.setAngle2Capture
        array0 = list(reversed(range(0, 91, angle)))
        array1 = list(reversed(range(angle,181-angle, angle)))
        array2 = [array1[-1]-angle]
        self.AngleCheck = array0+array1+array2
        for j in range (int(360/angle)-len(self.AngleCheck)):
            self.AngleCheck.append(180-(j+1)*angle)
        # print(self.AngleCheck)
        """Tạo mảng đánh dấu các mặt đã chụp ở các góc xoay tương ứng
        Ví dụ: Với các góc chụp nhứ trên, ảnh cần chụp sẽ là 4 ảnh, khi chưa chụp biến này sẽ có giá trị [0,0,0,0], 
        Khi mặt xoài đã chụp ở thời điểm mặt đầu quả xoài đang ở góc 90 độ lần thứ 2, biến này sẽ có giá trị [1,1,1,0]
        """
        self.FaceCheck = [0]*len(self.AngleCheck)
        self.Count_HalfRound = 0 #Biến điếm số lần quả xoài xoay được nửa vòng, do khi vừa vào buồng chụp, xoài vần còn rung lắc nên sử dụng biến này để không chụp vòng quay đầu tiên của quả xoài
        self.countCheck = 0 #Số thứ tự của góc chụp hiện tại trong mảng
        # self.previousRotate = 90 #Đặt góc xoay hiện tại cho vị trí chụp đầu tiên

    """ Tìm góc xoay và ảnh nhị phân mặt xoài
        Đầu vào hàm là khung ảnh từ camera 2
        Đầu ra hàm là giá trị True: Khi xoài có xoài và xoài nằm trong vùng làm việc, ngược lại là False
    """
    def find_Mango(self, frame):
        show = frame.copy()
        # self.point = [int(frame.shape[1]*0.38), int(frame.shape[0]*0.38)]
        # self.roisize = [int(100*0.38), int(100*0.38)]
        workArea = [self.point, [(self.point[0]+self.roisize[0]), (self.point[1]+self.roisize[1])]] #Tọa độ góc dưới bên phải của vùng làm việc
        cv2.rectangle(show, workArea[0], workArea[1], (0,0,255), 2) #vẽ vùng làm việc lên ảnh
        blur_frame = cv2.medianBlur(frame, 9) #Làm mờ bằng thuật toán medianBlur
        frame_LAB = cv2.cvtColor(blur_frame, cv2.COLOR_BGR2LAB)  # chuyển ảnh sang hệ màu Lab
        # cv2.imshow("fram_LAB", frame_LAB)
        threshLAB = cv2.inRange(frame_LAB, np.array(self.low_green), np.array(self.upp_green))  # tạo ảnh nhị phân theo ngưỡng
        # kernel = np.ones((10, 10), np.uint8)
        # threshLAB = cv2.erode(threshLAB, kernel, iterations=1)
        # threshLAB = cv2.dilate(threshLAB, kernel, iterations=1)
        
        contours, _ = cv2.findContours(threshLAB, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # tìm các đường contour
        """Khi không có quả xoài, thuật toán có thể không tìm thấy đường viền, nên có thể dẫn đến lỗi khi tìm đường viền lớn nhất,
           việc dùng try-except để bỏ quả qua lỗi không tìm thấy đường viền"""
        try:
            blank = np.zeros(frame.shape[:2], dtype=np.uint8) #Tạo ảnh đen có kích thước bằng với kích thước khung hình đã thu nhỏ
            contour = max(contours, key=cv2.contourArea) #Tìm đường viền lớn nhất của ảnh nhị phân
            cv2.drawContours(blank, [contour], 0, 255, -1) #vẽ đường viền lên ảnh đen để tạo thành ảnh nhị phân mặt xoài
            blank = cv2.erode(blank, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) #bào mòn ảnh nhị phân
            cv2.imshow('thresh', blank)
            contours, _ = cv2.findContours(blank, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #Tìm lại đường viền ảnh nhị phân vừa bào mòn
            ellipse = cv2.fitEllipse(contours[0]) #Tìm hình ellipse bao quanh quả xoài
            centerE = (int(ellipse[0][0]), int(ellipse[0][1])) #Tâm hình ellipse
            cv2.circle(show, centerE, 3, (0, 0, 255), 6) #Vẽ tâm hình ellipse lên quả xoài
            """"khi tâm quả xoài nằm trong vùng làm việc"""
            if cv2.contourArea(contour) > self.minArea_Mango and workArea[0][0] < centerE[0] < workArea[1][0] and workArea[0][1] < centerE[1] < workArea[1][1]:
                cv2.rectangle(show, workArea[0], workArea[1], (255,0,0), 2) #Đổi màu vùng làm việc
                self.rotation = ellipse[2] #Góc xoay hiện tại của quả xoài
                widthE = ellipse[1][0] #Kích thước trục chính lớn của hình ellipse
                """Tìm và vẽ tâm, góc xoay, trục chính lớn của hình ellipse"""
                x = (centerE[0] + widthE / 2 * np.sin(self.rotation*np.pi/180))
                y = (centerE[1] - widthE / 2 * np.cos(self.rotation*np.pi/180))
                cv2.circle(show, centerE, 3, (255, 0, 0), 6)
                cv2.putText(show, str(int(self.rotation))+"Deg",(int(centerE[0]) - 40, int(centerE[1]) - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0, 0, 255), 2, cv2.LINE_AA)
                cv2.line(show, centerE, (int(x), int(y)), (0, 0, 255), 2)
                return True, show
            else:
                return False, show
        except:
            return False, show
    
    """ Kiểm tra góc xoay quả xoài, dựa vào các góc xoay để đưa ra các lệnh tương ứng"""
    def check_Status(self):
        '''Kiểm tra góc xoay, do góc set đầu tiên có giá trị từ 0 đến 90 độ so với trục y, nên cần đặt góc lơn giá trị này để xoài xoay chậm trước khi bắt đầu thu ảnh'''
        if 160<self.rotation<=165:
            self.Count_HalfRound+=1
        
        '''Khi xoài đã xoay được một vòng'''
        if self.Count_HalfRound>=2:
            self.speedRotate='Medium' #Đặt lại tốc độ xoay xoài
            
            """TEST"""
            if self.rotation<=self.AngleCheck[self.countCheck]+3:
                self.check = True
                self.FaceCheck[self.countCheck]=1
                self.countCheck+=1
            else:
                self.check = False
            ''''''
            # if self.AngleCheck[self.countCheck]-self.setAngle2Capture-3< self.rotation <=self.AngleCheck[self.countCheck]+3 and self.AngleCheck[self.countCheck]!=0:
            #     if self.countCheck==0 and self.FaceCheck[self.countCheck]==0:#Thời điểm chụp là đầu tiên, thời điểm này chưa chụp ảnh
            #         self.check = True
            #         self.FaceCheck[self.countCheck]=1
            #     elif self.FaceCheck[self.countCheck-1]==1 and self.FaceCheck[self.countCheck]==0:#Nếu đã có ảnh chụp ở thời điểm trước đó và chưa có ảnh chụp ở thời điểm hiện tại
            #         self.check = True
            #         self.FaceCheck[self.countCheck]=1
            #     else: #khi không thõa các điều kiện ở trên
            #         self.check = False
            #     self.countCheck+=1
            # elif self.rotation>self.previousRotate and self.FaceCheck[self.countCheck-1]==1 and self.FaceCheck[self.countCheck]==0 and self.countCheck!=0:
            #     self.check = True
            #     self.FaceCheck[self.countCheck]=1
            #     self.countCheck+=1
            # else:
            #     self.check = False
            # self.previousRotate = self.rotation

            if self.FaceCheck[-1]==1: #Khi đã chụp ảnh cho thời điểm cuối cùng
                self.stopcheck = True
            else:
                self.stopcheck = False
            
        else: #Xoài chưa xoay được một vòng
            self.stopcheck = False
            self.check = False
            self.speedRotate='Max'
        
        return self.check, self.stopcheck, self.speedRotate
    
    """Đặt lại các biến như ban đầu sau khi hoàn thành tính diện tích khuyết điểm"""
    def resetStatus(self):
        angle = self.setAngle2Capture
        array0 = list(reversed(range(0, 91, angle)))
        array1 = list(reversed(range(angle,181-angle, angle)))
        array2 = [array1[-1]-angle]
        self.AngleCheck = array0+array1+array2
        for j in range (int(360/angle)-len(self.AngleCheck)):
            self.AngleCheck.append(180-(j+1)*angle)
        self.FaceCheck = [0]*len(self.AngleCheck)
        self.Count_HalfRound = 0
        self.countCheck = 0
        # self.previousRotate = 90

"""Kiểm tra chương trìhf con này
    CHỈ KẾT NỐI DUY NHẤT CAMERA 2
"""
if __name__ == "__main__":
    from BaslerCamera import camera
    import Module as mod

    cam = camera()
    # print(cam.framesizes)
    test = find([0, 0, 145], [255, 255, 255])
    cam.OpenCam()

    while cam.cameras.IsGrabbing:
        frame = cam.creatframe(0)
        frame = mod.Scale(frame, 0.09)
        mango, show = test.find_Mango(frame)
        # print(mango)

        if mango is True:
            save, stopcheck, keep = test.check_Status()
            # print(save, keep)

        cv2.imshow('Window', show)
        key = cv2.waitKey(1)
        if key == ord('q'):
            print("Stop acquiring camera")
            cv2.destroyAllWindows()
            break
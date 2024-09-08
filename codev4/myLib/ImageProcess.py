import codev4.myLib.Module as Mod
import numpy as np
import cv2

class Processing:
    def __init__(self, Center_Images, Scale_Center, Left_Images, Scale_Left, Right_Image, Scale_Right, Offset,
                  NumSlice_Center, NumSlice_Head, NumSlice_Tail, Box_Center, Box_LeftRight,
                  Func_ConstArea_Center, Func_ConstArea_Left, Func_ConstArea_Right,
                  Tape = False, CheckTape = [0,0,0]):
        self.Center_Images = Center_Images
        self.Left_Images = Left_Images
        self.Scale_Center = Scale_Center
        self.Scale_Left = Scale_Left
        self.Right_Image = Right_Image
        self.Scale_Right = Scale_Right
        self.Offset = Offset
        self.NumSlice_Center = NumSlice_Center
        self.NumSlice_Head = NumSlice_Head
        self.NumSlice_Tail = NumSlice_Tail
        self.Box_Center = Box_Center
        self.Box_LeftRight = Box_LeftRight

        self.Func_ConstArea_Center = Func_ConstArea_Center
        self.Func_ConstArea_Left = Func_ConstArea_Left
        self.Func_ConstArea_Right = Func_ConstArea_Right

        self.Tape = Tape
        self.CheckTape = CheckTape
        self.AllArea = []
        if Tape is True:
            self.minArea = 300
            self.maxArea = 3000
        else:
            self.minArea = 0
            self.maxArea = 3000

        self.Preprocess()
        self.SpecialPoints()
        self.INFSlicing()
        self.Slicing()
        self.LimitDefectArea()
        self.ConstAreaSlices()
        self.FindDefect()

    """TÌM ẢNH NHỊ PHÂN MẶT XOÀI, ĐƯỜNG VIỀN MẶT XOÀI, SỐ LÁT CẮT CHO TỪNG CAMERA"""
    def Preprocess(self):
        self.NumSlice_Left = None
        self.NumSlice_Right = None

        self.Faces_Crop_Center = []
        self.Cnts_RMstem_Center = []
        self.Masks_RMstem_Center = []
        self.X_Cut_Center = []
        self.Y_Cut_Center = []
        self.SizeCrop_Center = []
        self.Cordinate_BoxCenter = []

        self.Faces_Crop_Left = []
        self.Cnts_Mango_Left = []
        self.Masks_Mango_Left = []
        self.X_Cut_Left = []
        self.Y_Cut_Left = []
        self.SizeCrop_Left = []
        self.Cordinate_BoxLeft = []

        self.Face_Crop_Right = None
        self.Cnt_Mango_Right = None
        self.Mask_Mango_Right = None
        self.X_Cut_Right = None
        self.Y_Cut_Right = None
        self.SizeCrop_Right = None
        self.Cordinate_BoxRight = []

        
        for i in range(4): 
            """THU NHỎ ẢNH CAMEERA 1, 2"""               
            scale_centerfce = Mod.Scale(self.Center_Images[i],self.Scale_Center)
            scale_leftfce = Mod.Scale(self.Left_Images[i], self.Scale_Left)
            # cv2.imshow("Scale_Center", scale_centerfce)
            # cv2.imshow("Scale_Left", scale_leftfce)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            """TÌM ẢNH NHỊ PHÂN MẶT XOÀI CAMERA 1, 2"""
            mask_Mango_Center, mask_RMstem_Center = Mod.get_CenterMask(scale_centerfce)
            mask_Mango_Left = Mod.get_LeftMask(scale_leftfce)
            # cv2.imshow("Mask_Center", mask_Mango_Center)
            # cv2.imshow("RGB", scale_centerfce)
            # cv2.imshow("Mask_RMstem", mask_RMstem_Center)
            # cv2.imshow("Mask_Left", mask_Mango_Left)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            """DÙNG ẢNH ĐẦU TIÊN CỦA CAMERA 1 ĐỂ XÁC ĐỊNH VỊ TRÍ CUỐN XOÀI"""
            if i == 0:
                """TÌM ẢNH NHỊ PHÂN CUỐN XOÀI"""
                stem = cv2.bitwise_xor(mask_Mango_Center, mask_RMstem_Center)
                stem = cv2.erode(stem, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
                # cv2.imshow("Stem", stem)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
                contours_stem, _ = cv2.findContours(stem, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                # contours_stem, _ = cv2.findContours(mask_RMstem_Center, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                try:
                    cnt_stem = max(contours_stem, key=cv2.contourArea)
                except:
                    print('not stem')
                # M = cv2.moments(cnt_stem, True)
                # cX = int(M["m10"] / M["m00"])
                # cY = int(M["m01"] / M["m00"])
                # demo = scale_centerfce.copy()
                # cv2.circle(demo, (cX, cY), 3, (0,255,0), -1)
                # cv2.putText(demo, "("+str(cX)+","+str(cY)+")", (cX,cY+30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                # cv2.imshow("Tam cuan xoai",demo)

                # """CHỌN SỐ LÁT CẮT CHO TỪNG CAMERA"""
                # self.NumSlice_LimitCenter = int(0.5*self.NumSlice_Center)
                # if cX<mask_Mango_Center.shape[:2][1]/2:
                #     self.NumSlice_Left = self.NumSlice_Head
                #     self.NumSlice_Right = self.NumSlice_Tail
                #     self.NumSlice_LimitLeft = int(0.85*self.NumSlice_Head)
                #     self.NumSlice_LimitRight = int(0.95*self.NumSlice_Tail)
                # else:
                #     self.NumSlice_Right = self.NumSlice_Head
                #     self.NumSlice_Left = self.NumSlice_Tail
                #     self.NumSlice_LimitLeft = int(0.95*self.NumSlice_Tail)
                #     self.NumSlice_LimitRight = int(0.85*self.NumSlice_Head)

            """ĐƯỜNG VIỀN QUẢ XOÀI CỦA CAMERA 1, 2"""
            contours_Center, _ = cv2.findContours(mask_RMstem_Center, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours_Left, _ = cv2.findContours(mask_Mango_Left, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            contour_Center = max(contours_Center, key = cv2.contourArea)
            # demo = scale_centerfce.copy()
            # cv2.drawContours(demo, [contour_Center], 0, (0,255,0), 2)
            # cv2.imshow("duong vien lon nhat", demo)
            # cv2.waitKey(0)
            contour_Left = max(contours_Left, key = cv2.contourArea)
            # demo = scale_leftfce.copy()
            # cv2.drawContours(demo, [contour_Left], 0, (0,255,0), 2)
            # cv2.imshow("duong vien lon nhat", demo)
            # cv2.waitKey(0)

            """TÌM TỌA ĐỘ CẮT QUẢ XOÀI"""
            x1, y1, w1, h1 = cv2.boundingRect(contour_Center)
            # demodraw = scale_centerfce.copy()
            # cv2.rectangle(demodraw, (x1-self.Offset, y1-self.Offset), (x1+w1+self.Offset, y1+h1+self.Offset), (0,0, 255), 2)
            # cv2.imshow("1",demodraw)
            # cv2.waitKey(0)
            """Tọa độ ô vuông tìm khuyết điểm của camera 1"""
            div_w1= (w1+2*self.Offset)/self.Box_Center[0]
            div_h1 = (h1+2*self.Offset)/self.Box_Center[1]
            BoxThresh = []
            for j in range(self.Box_Center[1]):
                for k in range(self.Box_Center[0]):
                    point1 = (int(k*div_w1), int(j*div_h1))
                    point2 = (int((k+1)*div_w1),int((j+1)*div_h1))
                    BoxThresh.append([point1, point2])
            # print(f"Face{i}: {BoxThresh}")
            self.Cordinate_BoxCenter.append(BoxThresh)

            x2, y2, w2, h2 = cv2.boundingRect(contour_Left)
            # demodraw = scale_leftfce.copy()
            # cv2.rectangle(demodraw, (x2-self.Offset, y2-self.Offset), (x2+w2+self.Offset, y2+h2+self.Offset), (0,0,255), 2)
            # cv2.imshow("2",demodraw)
            # cv2.waitKey(0)
            """Tọa độ ô vuông tìm khuyết điểm của camera 2"""
            if i==2:
                div_w2= (w2+2*self.Offset)/self.Box_LeftRight[0]
                div_h2 = (h2+2*self.Offset)/self.Box_LeftRight[1]
                BoxThresh = []
                for j in range(self.Box_LeftRight[1]):
                    for k in range(self.Box_LeftRight[0]):
                        point1 = (int(k*div_w2), int(j*div_h2))
                        point2 = (int((k+1)*div_w2),int((j+1)*div_h2))
                        BoxThresh.append([point1, point2])
                # print(f"Face{i}: {BoxThresh}")
                self.Cordinate_BoxLeft.append(BoxThresh)

            x1_Offset = x1-self.Offset
            y1_Offset = y1-self.Offset
            w1_Offset = w1+2*self.Offset
            h1_Offset = h1+2*self.Offset

            x2_Offset = x2-self.Offset
            y2_Offset = y2-self.Offset
            w2_Offset = w2+2*self.Offset
            h2_Offset = h2+2*self.Offset

            self.X_Cut_Center.append(x1_Offset)
            self.Y_Cut_Center.append(y1_Offset)
            self.X_Cut_Left.append(x2_Offset)
            self.Y_Cut_Left.append(y2_Offset)

            """TÁCH QUẢ XOÀI CAMERA 1 RA KHỎI ẢNH"""
            crop_FaceCenter = scale_centerfce[y1_Offset:y1_Offset+h1_Offset, x1_Offset:x1_Offset+w1_Offset]
            crop_MaskCenter = mask_RMstem_Center[y1_Offset:y1_Offset+h1_Offset, x1_Offset:x1_Offset+w1_Offset]
            """TỌA ĐỘ ĐƯỜNG VIỀN CAMERA 1 SAU KHI TÁCH QUẢ XOÀI"""
            contour_Center[:, :, 0] = contour_Center[:, :, 0] - x1_Offset
            contour_Center[:, :, 1] = contour_Center[:, :, 1] - y1_Offset
            height_Center, width_Center = crop_FaceCenter.shape[:2]
            # demo = crop_FaceCenter.copy()
            # cv2.drawContours(demo, [contour_Center], 0, [0,255,0], 2)
            # cv2.imshow("contour", demo)
            # cv2.waitKey(0)
            # cv2.imshow("Crop_Center", crop_FaceCenter)
            # cv2.imshow("Crop_Mask_Center", crop_MaskCenter)

            """TÁCH QUẢ XOÀI CAMERA 2 RA KHỎI ẢNH"""
            crop_FaceLeft = scale_leftfce[y2_Offset:y2_Offset+h2_Offset, x2_Offset:x2_Offset+w2_Offset]
            crop_MaskLeft = mask_Mango_Left[y2_Offset:y2_Offset+h2_Offset, x2_Offset:x2_Offset+w2_Offset]
            """TỌA ĐỘ ĐƯỜNG VIỀN CAMERA 2 SAU KHI TÁCH QUẢ XOÀI"""
            contour_Left[:, :, 0] = contour_Left[:, :, 0] - x2_Offset
            contour_Left[:, :, 1] = contour_Left[:, :, 1] - y2_Offset
            height_Left, width_Left = crop_FaceLeft.shape[:2]
            # demo = crop_FaceLeft.copy()
            # cv2.drawContours(demo, [contour_Left], 0, [0,255,0], 2)
            # cv2.imshow("contour", demo)
            # cv2.waitKey(0)
            # cv2.imshow("Crop_mask_Left", crop_MaskLeft)
            # cv2.imshow("Crop_Left", crop_FaceLeft)

            self.Faces_Crop_Center.append(crop_FaceCenter)
            self.Cnts_RMstem_Center.append(contour_Center)
            self.Masks_RMstem_Center.append(crop_MaskCenter)
            
            self.Faces_Crop_Left.append(crop_FaceLeft)
            self.Cnts_Mango_Left.append(contour_Left)
            self.Masks_Mango_Left.append(crop_MaskLeft)

            self.SizeCrop_Center.append([width_Center, height_Center])
            self.SizeCrop_Left.append([width_Left, height_Left])

            """TÁCH QUẢ XOÀI TỪ CAMERA 3 RA KHỎI KHUNG HÌNH"""
            if self.Face_Crop_Right is None:
                """THU NHỎ ẢNH TỪ CAMERA 3"""
                scale_rightfce = Mod.Scale(self.Right_Image, self.Scale_Right)
                # cv2.imshow("Scale_Right", scale_rightfce)
                """TÌM ẢNH NHỊ PHÂN QUẢ XOÀI TỪ CAMERA 3"""
                mask_Mango_Right = Mod.get_RightMask(scale_rightfce)
                # cv2.imshow("Mask_Center", mask_Mango_Right)
                """ĐƯỜNG QUẢ XOÀI VIỀN CAMERA 3"""
                contours_Right, _ = cv2.findContours(mask_Mango_Right, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contour_Right = max(contours_Right, key = cv2.contourArea)
                # demo = scale_rightfce.copy()
                # cv2.drawContours(demo, [contour_Right], 0, (0,255,0), 2)
                # cv2.imshow("duong vien lon", demo)

                """TỌA ĐỘ TÁCH QUẢ XÒA"""
                x3, y3, w3, h3 = cv2.boundingRect(contour_Right)
                # demodraw = scale_rightfce.copy()
                # cv2.rectangle(demodraw, (x3-self.Offset, y3-self.Offset), (x3+w3+self.Offset, y3+h3+self.Offset), (0,0,255), 2)
                # cv2.imshow("demodraw",demodraw)

                """Tọa độ ô vuông tìm khuyết điểm của camera 3"""
                div_w3= (w3+2*self.Offset)/self.Box_LeftRight[0]
                div_h3 = (h3+2*self.Offset)/self.Box_LeftRight[1]
                BoxThresh = []
                for j in range(self.Box_LeftRight[1]):
                    for k in range(self.Box_LeftRight[0]):
                        point1 = (int(k*div_w3), int(j*div_h3))
                        point2 = (int((k+1)*div_w3),int((j+1)*div_h3))
                        BoxThresh.append([point1, point2])
                # print(f"Face{i}: {BoxThresh}")
                self.Cordinate_BoxRight.append(BoxThresh)

                x3_Offset = x3-self.Offset
                y3_Offset = y3-self.Offset
                w3_Offset = w3+2*self.Offset
                h3_Offset = h3+2*self.Offset
                self.X_Cut_Right = x3_Offset
                self.Y_Cut_Right = y3_Offset

                """TÁCH QUẢ XOÀI KHỎI KHUNG ẢNH"""
                self.Face_Crop_Right = scale_rightfce[y3_Offset:y3_Offset+h3_Offset, x3_Offset:x3_Offset+w3_Offset]
                self.Mask_Mango_Right = mask_Mango_Right[y3_Offset:y3_Offset+h3_Offset, x3_Offset:x3_Offset+w3_Offset]

                """TỌA ĐỘ ĐƯỜNG VIỀN SAU KHI TÁCH KHỎI KHUNG ẢNH"""
                contour_Right[:, :, 0] = contour_Right[:, :, 0] - x3_Offset
                contour_Right[:, :, 1] = contour_Right[:, :, 1] - y3_Offset
                self.Cnt_Mango_Right = contour_Right
                height_Right, width_Right = self.Face_Crop_Right.shape[:2]           
                self.SizeCrop_Right = [width_Right, height_Right]
                demo = self.Face_Crop_Right.copy()
                # cv2.drawContours(demo, [contour_Right], 0, [0,255,0], 2)
                # cv2.imshow("contour", demo)
                # cv2.waitKey(0)
            #     cv2.imshow("Crop_Right", self.Face_Crop_Right)
            #     cv2.imshow("Crop_mask_right", self.Mask_Mango_Right)
            # cv2.waitKey(0)

    """TÌM TRỌNG TÂM QUẢ XOÀI"""
    def SpecialPoints(self):
        self.TopLeftRight_Center = []
        self.TopLeftRight_Left = []
        self.TopLeftRight_Right = None
        self.Intersection_Center = []    #Điểm chứa thông tin khoảng cách gần nhất cho camera bên trái
        self.Intersection_Left = []      #Điểm chưa thông tin khoảng cách gần nhất cho camera giữa
        self.Intersection_Right = None

        """TÌM ĐIỂM TRÊN-DƯỚI-TRÁI-PHẢI, VÀ GIAO ĐIỂM CỦA NHỮNG ĐƯỜNG TẠO BỞI 4 ĐIỂM NÀY"""
        for i in range(4): 
            """CAMERA Ở GIỮA"""
            topmost_Center, leftmost_Center, rightmost_Center, bottommost_Center = Mod.find_TopBottomLeftRight(self.Cnts_RMstem_Center[i])
            intersection_Center = Mod.find_intersection_point((0, self.SizeCrop_Center[i][1]/2), (self.SizeCrop_Center[i][0], self.SizeCrop_Center[i][1]/2),
                                                              bottommost_Center, topmost_Center)
            """XÁC ĐỊNH ĐẦU/ĐUÔI CAMERA ĐANG HƯỚNG VỀ PHÍA NÀO CHỌN SỐ LÁT CẮT CHO TỪNG CAMERA"""
            if i==0:          
                self.NumSlice_LimitCenter = int(0.5*self.NumSlice_Center)
                if intersection_Center[0]<self.SizeCrop_Center[i][0]/2:
                    self.NumSlice_Left = self.NumSlice_Head
                    self.NumSlice_Right = self.NumSlice_Tail
                    self.NumSlice_LimitLeft = int(0.85*self.NumSlice_Head)
                    self.NumSlice_LimitRight = int(0.95*self.NumSlice_Tail)
                else:
                    self.NumSlice_Right = self.NumSlice_Head
                    self.NumSlice_Left = self.NumSlice_Tail
                    self.NumSlice_LimitLeft = int(0.95*self.NumSlice_Tail)
                    self.NumSlice_LimitRight = int(0.85*self.NumSlice_Head)

            """CAMERA BÊN TRÁI"""
            topmost_Left, leftmost_Left, rightmost_Left, bottommost_Left = Mod.find_TopBottomLeftRight(self.Cnts_Mango_Left[i])
            # intersection_Left = Mod.find_intersection_point(rightmost_Left, leftmost_Left, bottommost_Left, topmost_Left)
            intersection_Left = (self.SizeCrop_Left[i][0]/2, self.SizeCrop_Left[i][1]/2)
            """CAMERA BÊN PHẢI"""
            if self.TopLeftRight_Right is None:
                topmost_Right, leftmost_Right, rightmost_Right, bottommost_Right = Mod.find_TopBottomLeftRight(self.Cnt_Mango_Right)
                # intersection_Right = Mod.find_intersection_point(rightmost_Right, leftmost_Right, bottommost_Right, topmost_Right)
                intersection_Right = (self.SizeCrop_Right[0]/2, self.SizeCrop_Right[1]/2)
                self.TopLeftRight_Right = [topmost_Right, leftmost_Right, rightmost_Right, bottommost_Right]
                self.Intersection_Right = intersection_Right
            """ĐƯA DỮ LIỆU VÀO MẢNG"""
            self.TopLeftRight_Center.append([topmost_Center, leftmost_Center, rightmost_Center, bottommost_Center])
            self.TopLeftRight_Left.append([topmost_Left, leftmost_Left, rightmost_Left, bottommost_Left])
            self.Intersection_Center.append(intersection_Center)
            self.Intersection_Left.append(intersection_Left)


        """THỂ HIỆN LÊN HÌNH VẼ"""
        # for i in range(4):
        #     demo_center = self.Faces_Crop_Center[i].copy()
        #     demo_left = self.Faces_Crop_Left[i].copy()
        #     demo_right = self.Face_Crop_Right.copy()
            
        #     # cv2.line(img=demo_center, pt1 = self.TopLeftRight_Center[i][0], pt2=self.TopLeftRight_Center[i][3], color=(255,0,0), thickness=1)
        #     # cv2.line(img=demo_center, pt1 = self.TopLeftRight_Center[i][1], pt2=self.TopLeftRight_Center[i][2], color=(255,0,0), thickness=1)
        #     cv2.circle(img = demo_center, center = self.TopLeftRight_Center[i][0], radius=5, color=(0, 255, 0), thickness=-1)
        #     cv2.circle(img = demo_center, center = self.TopLeftRight_Center[i][1], radius=5, color=(0, 255, 0), thickness=-1)
        #     cv2.circle(img = demo_center, center = self.TopLeftRight_Center[i][2], radius=5, color=(0, 255, 0), thickness=-1)
        #     cv2.circle(img = demo_center, center = self.TopLeftRight_Center[i][3], radius=5, color=(0, 255, 0), thickness=-1)
        #     cv2.circle(img = demo_center, center = (int(self.Intersection_Center[i][0]),int(self.Intersection_Center[i][1])), radius=5, color=(0, 0, 255), thickness=-1)

        #     # cv2.line(img=demo_left, pt1 = self.TopLeftRight_Left[i][0], pt2=self.TopLeftRight_Left[i][3], color=(255,0,0), thickness=1)
        #     # cv2.line(img=demo_left, pt1 = self.TopLeftRight_Left[i][1], pt2=self.TopLeftRight_Left[i][2], color=(255,0,0), thickness=1)
        #     cv2.circle(img = demo_left, center = self.TopLeftRight_Left[i][0], radius=5, color=(0, 255, 0), thickness=-1)
        #     cv2.circle(img = demo_left, center = self.TopLeftRight_Left[i][1], radius=5, color=(0, 255, 0), thickness=-1)
        #     cv2.circle(img = demo_left, center = self.TopLeftRight_Left[i][2], radius=5, color=(0, 255, 0), thickness=-1)
        #     cv2.circle(img = demo_left, center = self.TopLeftRight_Left[i][3], radius=5, color=(0, 255, 0), thickness=-1)
        #     cv2.circle(img = demo_left, center = (int(self.Intersection_Left[i][0]),int(self.Intersection_Left[i][1])), radius=5, color=(0, 0, 255), thickness=-1)

        #     # cv2.line(img=demo_right, pt1 = self.TopLeftRight_Right[0], pt2=self.TopLeftRight_Right[3], color=(0,0,255), thickness=1)
        #     # cv2.line(img=demo_right, pt1 = self.TopLeftRight_Right[1], pt2=self.TopLeftRight_Right[2], color=(0,0,255), thickness=1)
        #     cv2.circle(img = demo_right, center = self.TopLeftRight_Right[0], radius=5, color=(0, 255, 0), thickness=-1)
        #     cv2.circle(img = demo_right, center = self.TopLeftRight_Right[1], radius=5, color=(0, 255, 0), thickness=-1)
        #     cv2.circle(img = demo_right, center = self.TopLeftRight_Right[2], radius=5, color=(0, 255, 0), thickness=-1)
        #     cv2.circle(img = demo_right, center = self.TopLeftRight_Right[3], radius=5, color=(0, 255, 0), thickness=-1)
        #     cv2.circle(img = demo_right, center = (int(self.Intersection_Right[0]),int(self.Intersection_Right[1])), radius=5, color=(0, 0, 255), thickness=-1)

        #     win1 = Mod.stackImages([demo_center, demo_left, demo_right], mode = 0)
        #     win2 = Mod.stackImages([self.Masks_RMstem_Center[i], self.Masks_Mango_Left[i], self.Mask_Mango_Right], mode=0)

        #     cv2.imshow("window 1", win1)
        #     cv2.imshow("window 2", win2)
        #     cv2.waitKey(0)

    """TÌM HÌNH CHIẾU LÁT CẮT"""
    def INFSlicing(self):
        """THÔNG TIN LÁT CẮT CHO CAMERA GIỮA"""
        self.SliceHeight_CenterFaces= []
        self.RatioWidthHeigthSlice_Center = []
        self.SliceOffset_Center = []
        self.SlicePoint_CenterFaces = []
        for i in range(4):
            SliceHeight_Face = []
            widthheight_slice= []
            Slice_Points = []
            """KHOẢNG CÁCH GIỮA CÁC LÁT CẮT"""
            if i!=3:
                nextface = i+1
            else:
                nextface = 0
            # cv2.imshow('right', self.Faces_Crop_Center[nextface])
            # cv2.imshow('front', self.Faces_Crop_Left[i])
            # cv2.waitKey(0)
            """khoảng cách từng lát cắt trên camera 2"""
            Div_inter2top_Left = (self.Intersection_Left[i][1]-self.TopLeftRight_Left[i][0][1])/self.NumSlice_Center
            """khoảng cách từng lát cắt trên ảnh vuông góc liền kề với camera 1"""
            Div_inter2left_NextCenter = (self.Intersection_Center[nextface][1]-self.TopLeftRight_Center[nextface][0][1])/self.NumSlice_Center

            """tìm độ cao lát cắt, giao điểm của đường thẳng y = z với đường viền quả xoài"""
            for j in range(self.NumSlice_Center):
                if i!=3:
                    nextface = i+1
                else:
                    nextface = 0
                """theo trục x"""
                Z1 = self.Intersection_Center[nextface][1]-j*(Div_inter2left_NextCenter)
                start_point1, end_point1, start_point2, end_point2 = Mod.points_nearest_line(contour = self.Cnts_RMstem_Center[nextface], a = Z1, axis=1)              
                point1 = Mod.find_intersection_point(start_point1, end_point1, (0, int(Z1)), (self.SizeCrop_Center[nextface][0],int(Z1)))
                point2 = Mod.find_intersection_point(start_point2, end_point2, (0, int(Z1)), (self.SizeCrop_Center[nextface][0],int(Z1)))
                """theo trục y"""
                Z0 = self.Intersection_Left[i][1]-j*(Div_inter2top_Left)
                start_point1, end_point1, start_point2, end_point2 = Mod.points_nearest_line(contour=self.Cnts_Mango_Left[i], a = Z0, axis = 1)
                point3 = Mod.find_intersection_point(start_point1, end_point1, (0, int(Z0)), (self.SizeCrop_Center[0][0],int(Z0)))
                point4 = Mod.find_intersection_point(start_point2, end_point2, (0, int(Z0)), (self.SizeCrop_Center[0][0],int(Z0)))
                """kích thước từng lát cắt theo truc x, trục y"""
                widthheight_slice.append([np.abs(point2[0]-point1[0]), np.abs(point4[0]-point3[0])])
                """tọa độ lát cắt ( TỌA ĐỔ ĐỂ TÍNH HỆ SỐ DIỆN TÍCH CHO LÁT CẮT)"""
                SliceHeight_Face.append((Z0+self.Y_Cut_Left[i])/self.Scale_Left)
                """tọa độ điểm của lát cắt, 2 điểm đầu của hình chiếu lát cắt theo trục x, 2 điểm sau của hình chiếu lát cắt theo trục y"""
                Slice_Points.append([point1, point2, point3, point4])

            self.SliceHeight_CenterFaces.append(SliceHeight_Face)
            self.SlicePoint_CenterFaces.append(Slice_Points)
            ratio_widthheight = []
            slice_offset = []
            """tỷ lệ lát cắt thứ i với lát cắt đầu tiên"""
            for j in range(len(widthheight_slice)):
                """tỷ lệ thu nhỏ theo trục x, trục y"""
                ratio_widthheight.append([widthheight_slice[j][0]/widthheight_slice[0][0], widthheight_slice[j][1]/widthheight_slice[0][1]])
                """tọa độ dịch chuyển lát cắt theo trục x, trục y"""
                if i!=3:
                    nextface = i+1
                else:
                    nextface = 0
                slice_offset.append([self.SizeCrop_Center[i][0]*((Slice_Points[j][0][0]-Slice_Points[0][0][0])/self.SizeCrop_Center[nextface][0]), 
                                    self.SizeCrop_Center[i][1]*((Slice_Points[j][2][0]-Slice_Points[0][2][0])/self.SizeCrop_Left[i][0])])
            self.RatioWidthHeigthSlice_Center.append(ratio_widthheight)
            self.SliceOffset_Center.append(slice_offset)

        """THÔNG TIN LẮT CẮT CHO CAMERA BÊN TRÁI"""
        self.SliceHeight_LeftFace= []
        self.RatioWidthHeigthSlice_Left = []
        self.SliceOffset_Left = []
        self.SlicePoint_LeftFaces = []
        widthheight_slice = []
        # cv2.imshow('0', self.Faces_Crop_Left[2])
        # cv2.imshow('1', self.Faces_Crop_Center[2])
        # cv2.imshow('2', self.Faces_Crop_Center[3])
        # cv2.waitKey(0)
    
        """tìm khoảng cách giữa các lát cắt theo theo trục x, trục y"""
        Div_inter2left_BigFce = (self.Intersection_Center[2][0]-self.TopLeftRight_Center[2][1][0])/self.NumSlice_Left
        Div_inter2left_SmallFce = (self.Intersection_Center[3][0]-self.TopLeftRight_Center[3][1][0])/self.NumSlice_Left
        for i in range(self.NumSlice_Left):
            """tọa độ hình chiếu của lát cắt trên mặt bụng và mặt lưng"""
            Z0 = self.Intersection_Center[2][0]-i*Div_inter2left_BigFce
            Z1 = self.Intersection_Center[3][0]-i*Div_inter2left_SmallFce
            """tìm tọa độ giao điểm của đường thẳng x = z với đường viền quả xoài"""
            start_point1, end_point1, start_point2, end_point2 = Mod.points_nearest_line(contour = self.Cnts_RMstem_Center[2], a = Z0, axis=0)
            point1 = Mod.find_intersection_point(start_point1, end_point1, (int(Z0), 0), (int(Z0), self.SizeCrop_Center[2][1]))
            point2 = Mod.find_intersection_point(start_point2, end_point2, (int(Z0), 0), (int(Z0), self.SizeCrop_Center[2][1]))
            start_point1, end_point1, start_point2, end_point2 = Mod.points_nearest_line(contour = self.Cnts_RMstem_Center[1], a = Z1, axis=0)
            point3 = Mod.find_intersection_point(start_point1, end_point1, (int(Z1), 0), (int(Z1), self.SizeCrop_Center[3][1]))
            point4 = Mod.find_intersection_point(start_point2, end_point2, (int(Z1), 0), (int(Z1), self.SizeCrop_Center[3][1]))
            self.SlicePoint_LeftFaces.append([point1, point2, point3, point4])
            self.SliceHeight_LeftFace.append((Z0+self.X_Cut_Center[2])/self.Scale_Center)
            widthheight_slice.append([np.abs(point2[1]-point1[1]), np.abs(point4[1]-point3[1])])

        # print(self.SliceHeight_LeftFace)
        for j in range(len(widthheight_slice)):
            """tìm tỷ lệ lát cắt theo trục z, trục y"""
            self.RatioWidthHeigthSlice_Left.append([widthheight_slice[j][0]/widthheight_slice[0][0], widthheight_slice[j][1]/widthheight_slice[0][1]])
            """timg tọa độ dịch lát căt theo trục x, trục y"""
            self.SliceOffset_Left.append([self.SizeCrop_Left[2][0]*(self.SlicePoint_LeftFaces[j][0][1]-self.SlicePoint_LeftFaces[0][0][1])/self.SizeCrop_Center[2][1],
                                          self.SizeCrop_Left[2][1]*(self.SlicePoint_LeftFaces[j][2][1]-self.SlicePoint_LeftFaces[0][2][1])/self.SizeCrop_Center[1][1]])
 
        """THÔNG TIN CẮT LÁT CHO CAMERA BÊN PHẢI""" 
        self.SliceHeight_RightFace= []
        self.RatioWidthHeigthSlice_Right = []
        self.SliceOffset_Right = []
        self.SlicePoint_RightFaces = []
        widthheight_slice = []
        Div_inter2right_BigFce = (self.TopLeftRight_Center[2][2][0]-self.Intersection_Center[2][0])/self.NumSlice_Right
        Div_inter2right_SmallFce = (self.TopLeftRight_Center[1][2][0]-self.Intersection_Center[1][0])/self.NumSlice_Right
        for i in range(self.NumSlice_Right):
            """tọa độ hình chiếu của lát cắt trên mặt bụng và mặt lưng"""
            # cv2.imshow('0', self.Faces_Crop_Center[2])
            # cv2.imshow('1', self.Faces_Crop_Center[1])
            # cv2.imshow('2', self.Face_Crop_Right)
            # cv2.waitKey(0)
            Z0 = self.Intersection_Center[2][0]+i*Div_inter2right_BigFce
            Z1 = self.Intersection_Center[1][0]+i*Div_inter2right_SmallFce
            """tìm tọa độ giao điểm của đường thẳng x = z với đường viền quả xoài"""
            start_point1, end_point1, start_point2, end_point2 = Mod.points_nearest_line(contour = self.Cnts_RMstem_Center[2], a = Z0, axis=0)
            point1 = Mod.find_intersection_point(start_point1, end_point1, (int(Z0), 0), (int(Z0), self.SizeCrop_Center[2][1]))
            point2 = Mod.find_intersection_point(start_point2, end_point2, (int(Z0), 0), (int(Z0), self.SizeCrop_Center[2][1]))
            start_point1, end_point1, start_point2, end_point2 = Mod.points_nearest_line(contour = self.Cnts_RMstem_Center[3], a = Z1, axis=0)
            point3 = Mod.find_intersection_point(start_point1, end_point1, (int(Z1), 0), (int(Z1), self.SizeCrop_Center[1][1]))
            point4 = Mod.find_intersection_point(start_point2, end_point2, (int(Z1), 0), (int(Z1), self.SizeCrop_Center[1][1]))

            self.SlicePoint_RightFaces.append([point1, point2, point3, point4])
            self.SliceHeight_RightFace.append((Z0+self.X_Cut_Center[2])/self.Scale_Center)
            widthheight_slice.append([np.abs(point2[1]-point1[1]), np.abs(point4[1]-point3[1])])
        # print(self.SliceHeight_RightFace)

        for j in range(len(widthheight_slice)):
            """tìm tỷ lệ lát cắt theo trục x, trục y"""
            self.RatioWidthHeigthSlice_Right.append([widthheight_slice[j][0]/widthheight_slice[0][0], widthheight_slice[j][1]/widthheight_slice[0][1]])
            """tìm tọa độ dịch lát cắt theo trục x, trục y"""
            self.SliceOffset_Right.append([self.SizeCrop_Right[0]*(self.SlicePoint_RightFaces[0][1][1]-self.SlicePoint_RightFaces[j][1][1])/self.SizeCrop_Center[2][1],
                                          self.SizeCrop_Right[1]*(self.SlicePoint_RightFaces[0][3][1]-self.SlicePoint_RightFaces[j][3][1])/self.SizeCrop_Center[3][1]])

    
        """LÁT CẮT CỦA CAMERA GIỮA KHI NHÌN TỪ CAMERA BÊN TRÁI VÀ TẤM ẢNH TIẾP THEO CỦA CAMERA GIỮA"""
        # for i in range(4):
        #     demo_Left = self.Faces_Crop_Left[i].copy()
        #     # cv2.drawContours(demo_Left, [self.Cnts_Mango_Left[i]], 0, (0,0, 255), 2)
        #     if i!=3:
        #         demo_nextCenter = self.Faces_Crop_Center[i+1].copy()
        #         mask_nextCenter = self.Masks_RMstem_Center[i+1]
        #         # cv2.drawContours(demo_nextCenter, [self.Cnts_RMstem_Center[i+1]], 0, (0,0, 255), 2)
        #     else:
        #         demo_nextCenter = self.Faces_Crop_Center[0].copy()
        #         mask_nextCenter = self.Masks_RMstem_Center[0]
        #         # cv2.drawContours(demo_nextCenter, [self.Cnts_RMstem_Center[0]], 0, (0,0, 255), 2)
            
            

        #     for point in self.SlicePoint_CenterFaces[i]:
        #         # # demo_nextCenter_1 = self.Faces_Crop_Center[i+1].copy()
        #         # # cv2.line(img = demo_nextCenter_1, pt1 = (int(point[0][0]),int(point[0][1])), pt2 = (int(point[1][0]),int(point[1][1])), color=(255,255, 0), thickness=1)
        #         # # cv2.imshow("deomo", demo_nextCenter_1)
        #         # # cv2.waitKey(0)
        #         # demo_Left = self.Faces_Crop_Left[i].copy()
        #         # if i!=3:
        #         #     demo_nextCenter = self.Faces_Crop_Center[i+1].copy()
        #         #     mask_nextCenter = self.Masks_RMstem_Center[i+1]
        #         #     cv2.circle(img = demo_nextCenter, center = (int(self.Intersection_Center[i+1][0]),int(self.Intersection_Center[i+1][1])), radius=4, color=(0, 0, 255), thickness=-4)
        #         #     # cv2.drawContours(demo_nextCenter, [self.Cnts_RMstem_Center[i+1]], 0, (0,0, 255), 2)
        #         # else:
        #         #     demo_nextCenter = self.Faces_Crop_Center[0].copy()
        #         #     mask_nextCenter = self.Masks_RMstem_Center[0]
        #         #     cv2.circle(img = demo_nextCenter, center = (int(self.Intersection_Center[0][0]),int(self.Intersection_Center[0][1])), radius=4, color=(0, 0, 255), thickness=-4)

        #         cv2.circle(img = demo_Left, center = (int(self.Intersection_Left[i][0]),int(self.Intersection_Left[i][1])), radius=4, color=(0, 0, 255), thickness=-3)    
        #         cv2.line(img = demo_nextCenter, pt1 = (int(point[0][0]),int(point[0][1])), pt2 = (int(point[1][0]),int(point[1][1])), color=(255,255, 0), thickness=2)
        #         cv2.line(img = demo_Left, pt1 = (int(point[2][0]),int(point[2][1])), pt2 = (int(point[3][0]),int(point[3][1])), color=(255,255, 0), thickness=2)
        #         cv2.circle(img = demo_nextCenter, center = (int(point[0][0]),int(point[0][1])), radius=3, color=(0, 0, 255), thickness=-1)
        #         cv2.circle(img = demo_nextCenter, center = (int(point[1][0]),int(point[1][1])), radius=3, color=(0, 0, 255), thickness=-1)
        #         cv2.circle(img = demo_Left, center = (int(point[2][0]),int(point[2][1])), radius=3, color=(0, 0, 255), thickness=-1)
        #         cv2.circle(img = demo_Left, center = (int(point[3][0]),int(point[3][1])), radius=3, color=(0, 0, 255), thickness=-1)
        #     cv2.imshow("Center0",self.Faces_Crop_Center[i])
        #     cv2.imshow("Left", demo_Left)
        #     cv2.imshow("Center", demo_nextCenter)
        #     cv2.imshow("Mask curent", self.Masks_RMstem_Center[i])
        #     cv2.imshow("Mask_next", mask_nextCenter)
        #     cv2.imshow("Mask left", self.Masks_Mango_Left[i])
        #     cv2.waitKey(0)
        #     cv2.destroyAllWindows()

        """LÁT CẮT CỦA CAMERA TRÁI KHI NHÌN TỪ CAMERA GIỮA"""
        # demo_center_0 = self.Faces_Crop_Center[2].copy()
        # demo_center_1 = self.Faces_Crop_Center[3].copy()

        # for point in self.SlicePoint_LeftFaces:
        #     # demo_nextCenter_1 = self.Faces_Crop_Center[3].copy()
        #     # cv2.circle(img = demo_nextCenter_1, center = (int(point[2][0]),int(point[2][1])), radius=2, color=(0, 0, 255), thickness=-1)
        #     # cv2.circle(img = demo_nextCenter_1, center = (int(point[3][0]),int(point[3][1])), radius=2, color=(0, 0, 255), thickness=-1)
        #     # cv2.line(img = demo_nextCenter_1, pt1 = (int(point[2][0]),int(point[2][1])), pt2 = (int(point[3][0]),int(point[3][1])), color=(255,255, 0), thickness=1)
        #     # cv2.circle(img = demo_nextCenter_1, center = (int(self.Intersection_Center[3][0]),int(self.Intersection_Center[3][1])), radius=4, color=(0, 0, 255), thickness=-1)
        #     # cv2.imshow("deomo", demo_nextCenter_1)
        #     # cv2.waitKey(0)
        #     # demo_center_0 = self.Faces_Crop_Center[2].copy()
        #     # demo_center_1 = self.Faces_Crop_Center[3].copy()
        #     cv2.line(img = demo_center_0, pt1 = (int(point[0][0]),int(point[0][1])), pt2 = (int(point[1][0]),int(point[1][1])), color=(0,255, 0), thickness=2)
        #     cv2.line(img = demo_center_1, pt1 = (int(point[2][0]),int(point[2][1])), pt2 = (int(point[3][0]),int(point[3][1])), color=(0,255, 0), thickness=2)
        #     cv2.circle(img = demo_center_0, center = (int(self.Intersection_Center[2][0]),int(self.Intersection_Center[2][1])), radius=4, color=(0, 0, 255), thickness=-1)
        #     cv2.circle(img = demo_center_1, center = (int(self.Intersection_Center[3][0]),int(self.Intersection_Center[3][1])), radius=4, color=(0, 0, 255), thickness=-1)
        #     cv2.circle(img = demo_center_0, center = (int(point[0][0]),int(point[0][1])), radius=3, color=(0, 0, 255), thickness=-1)
        #     cv2.circle(img = demo_center_0, center = (int(point[1][0]),int(point[1][1])), radius=3, color=(0, 0, 255), thickness=-1)
        #     cv2.circle(img = demo_center_1, center = (int(point[2][0]),int(point[2][1])), radius=3, color=(0, 0, 255), thickness=-1)
        #     cv2.circle(img = demo_center_1, center = (int(point[3][0]),int(point[3][1])), radius=3, color=(0, 0, 255), thickness=-1)
        
        # cv2.imshow("Left", self.Faces_Crop_Left[2])
        # cv2.imshow("Center 0", demo_center_0)
        # cv2.imshow("Center 1", demo_center_1)
        # cv2.imshow("massk0", self.Masks_RMstem_Center[2])
        # cv2.imshow("massk1", self.Masks_RMstem_Center[3])
        # cv2.waitKey(0)
        # cv2.destroyAllWindows() 

        """LÁT CẮT CỦA CAMERA PHẢI KHI NHÌN TỪ CAMERA GIỮA"""
        # demo_center_0 = self.Faces_Crop_Center[2].copy()
        # demo_center_1 = self.Faces_Crop_Center[1].copy()

        # for point in self.SlicePoint_RightFaces:
        #     # demo_center_2 = self.Faces_Crop_Center[2].copy()
        #     # demo_center_2 = cv2.line(img = demo_center_2, pt1 = (int(point[0][0]),int(point[0][1])), pt2 = (int(point[1][0]),int(point[1][1])), color=(0,255, 0), thickness=1)
        #     # cv2.imshow("Center 2", demo_center_2)
        #     # cv2.waitKey(0)
        #     # demo_center_0 = self.Faces_Crop_Center[2].copy()
        #     # demo_center_1 = self.Faces_Crop_Center[1].copy()
        #     cv2.line(img = demo_center_0, pt1 = (int(point[0][0]),int(point[0][1])), pt2 = (int(point[1][0]),int(point[1][1])), color=(0,255, 0), thickness=2)
        #     cv2.line(img = demo_center_1, pt1 = (int(point[2][0]),int(point[2][1])), pt2 = (int(point[3][0]),int(point[3][1])), color=(0,255, 0), thickness=2)
        #     cv2.circle(img = demo_center_0, center = (int(self.Intersection_Center[2][0]),int(self.Intersection_Center[2][1])), radius=4, color=(0, 0, 255), thickness=-1)
        #     cv2.circle(img = demo_center_1, center = (int(self.Intersection_Center[3][0]),int(self.Intersection_Center[3][1])), radius=4, color=(0, 0, 255), thickness=-1)
        #     cv2.circle(img = demo_center_0, center = (int(point[0][0]),int(point[0][1])), radius=3, color=(0, 0, 255), thickness=-1)
        #     cv2.circle(img = demo_center_0, center = (int(point[1][0]),int(point[1][1])), radius=3, color=(0, 0, 255), thickness=-1)
        #     cv2.circle(img = demo_center_1, center = (int(point[2][0]),int(point[2][1])), radius=3, color=(0, 0, 255), thickness=-1)
        #     cv2.circle(img = demo_center_1, center = (int(point[3][0]),int(point[3][1])), radius=3, color=(0, 0, 255), thickness=-1)
        # cv2.imshow("Right", self.Face_Crop_Right)
        # cv2.imshow("Center 0", demo_center_0)
        # cv2.imshow("Center 1", demo_center_1)
        # cv2.imshow("massk0", self.Masks_RMstem_Center[0])
        # cv2.imshow("massk1", self.Masks_RMstem_Center[1])
        # cv2.waitKey(0)
        # cv2.destroyAllWindows() 

    """CẮT LÁT QUẢ XOÀI"""
    def Slicing(self):
        """CẮT LÁT ẢNH CAMERA GIỮA"""
        self.Slices_Center = []
        self.SlicedFace_Center = []
        self.Intensity_Center = []
        self.ContourSlices_Center = []
        for i in range(4):
            SlicedFace, Slices, Intensity, ContourSlice = Mod.slice_Face(NumSlice=self.NumSlice_Center, Width=self.SizeCrop_Center[i][0], Height=self.SizeCrop_Center[i][1],
                                                           Contour=self.Cnts_RMstem_Center[i], Ratio_Scale=self.RatioWidthHeigthSlice_Center[i], Offset_Slice=self.SliceOffset_Center[i])
            self.Slices_Center.append(Slices)
            self.SlicedFace_Center.append(SlicedFace)
            self.Intensity_Center.append(Intensity)
            self.ContourSlices_Center.append(ContourSlice)
            # cv2.imshow("Sliced Face",SlicedFace)
            # cv2.imshow("Face", self.Faces_Crop_Center[i])
            # cv2.waitKey(0)
        """CẮT LÁT ẢNH CAMERA TRÁI"""
        self.Slices_Left = None
        self.SlicedFace_Left = None
        self.Intensity_Left = None
        self.ContourSlices_Left = None

        SlicedFace, Slices, Intensity, ContourSlice = Mod.slice_Face(NumSlice=self.NumSlice_Left, Width=self.SizeCrop_Left[2][0], Height=self.SizeCrop_Left[2][1],
                                                       Contour = self.Cnts_Mango_Left[2], Ratio_Scale=self.RatioWidthHeigthSlice_Left, Offset_Slice=self.SliceOffset_Left,
                                                       center_y=True)
        self.Slices_Left = Slices
        self.Intensity_Left = Intensity
        self.SlicedFace_Left=SlicedFace
        self.ContourSlices_Left=ContourSlice
        # cv2.imshow("Sliced Face Left",self.SlicedFace_Left)
        # cv2.imshow("Face Left", self.Faces_Crop_Left[2])
        # cv2.imshow("Face Center 0", self.Faces_Crop_Center[2])
        # cv2.imshow("Face Center 1", self.Faces_Crop_Center[3])
        # cv2.waitKey(0)

        """CẮT LÁT ẢNH CAMERA PHẢI"""
        self.Slices_Right = None
        self.SlicedFace_Right = None
        self.Intensity_Right = None
        self.ContourSlices_Right = None
        SlicedFace, Slices, Intensity, ContourSlice = Mod.slice_Face(NumSlice=self.NumSlice_Right, Width=self.SizeCrop_Right[0], Height=self.SizeCrop_Right[1],
                                                       Contour = self.Cnt_Mango_Right, Ratio_Scale=self.RatioWidthHeigthSlice_Right, Offset_Slice=self.SliceOffset_Right,
                                                       center_y=True)
        self.Slices_Right = Slices
        self.Intensity_Right = Intensity
        self.SlicedFace_Right=SlicedFace
        self.ContourSlices_Right=ContourSlice
        # cv2.imshow("Sliced Face Right",self.SlicedFace_Right)
        # cv2.imshow("Face Right", self.Face_Crop_Right)
        # cv2.imshow("Face Center 0", self.Faces_Crop_Center[2])
        # cv2.imshow("Face Center 1", self.Faces_Crop_Center[1])
        # cv2.waitKey(0)        

    """GIỚI HẠN VÙNG TÌM KHUYẾT ĐIỂM"""
    def LimitDefectArea(self):
        self.Contour_LimitCenter = []
        self.Contour_LimitLeft = None
        self.Contour_LimitRight = None
        """GIỚI HẠN TRÊN CAMERA GIỮA"""
        for i in range(0, 4):
            '''Phần còn lại sau khi giới hạn mặt đầu và đuôi'''
            mask1 = np.zeros((self.SizeCrop_Center[i][1], self.SizeCrop_Center[i][0]), dtype=np.uint8)
            x1 = int(self.SizeCrop_Center[i][0]*(self.SlicePoint_LeftFaces[self.NumSlice_LimitLeft][0][0]/self.SizeCrop_Center[2][0]))
            x2 = int(self.SizeCrop_Center[i][0]*(self.SlicePoint_RightFaces[self.NumSlice_LimitRight][0][0]/self.SizeCrop_Center[2][0]))
            cv2.rectangle(mask1, (x1, 0), (x2, self.SizeCrop_Center[i][1]), 255, -1)

            # demodraw = self.Faces_Crop_Center[i].copy()
            # demodraw = cv2.bitwise_and(demodraw, demodraw, mask = mask1)
            # cv2.imshow("mask", mask1)
            # cv2.imshow("test", demodraw)
            # cv2.waitKey(0)
            '''giới hạn trên mặt bụng, lưng'''
            if i == 0 or i == 2:#mặt bụng
                mask0 = self.Slices_Center[i][self.NumSlice_LimitCenter-1]
            else:
                mask0 = np.zeros((self.SizeCrop_Center[i][1], self.SizeCrop_Center[i][0]), dtype=np.uint8)
                if i == 1:
                    y1 = int(self.SlicePoint_CenterFaces[0][self.NumSlice_LimitCenter][0][1])
                    y2 = int(self.SizeCrop_Center[3][1]-self.SlicePoint_CenterFaces[2][self.NumSlice_LimitCenter][0][1])
                else:
                    y1 = int(self.SlicePoint_CenterFaces[2][self.NumSlice_LimitCenter][0][1])
                    y2 = int(self.SizeCrop_Center[1][1]-self.SlicePoint_CenterFaces[0][self.NumSlice_LimitCenter][0][1])
                cv2.rectangle(mask0, (0, y1), (self.SizeCrop_Center[i][0], y2), 255, -1)
            maskLimt = cv2.bitwise_and(mask0, mask1)                
            contours, _ = cv2.findContours(maskLimt, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            self.Contour_LimitCenter.append(max(contours, key = cv2.contourArea))

            # demo_draw = self.Faces_Crop_Center[i].copy()
            # # cv2.drawContours(demo_draw, [self.ContourSlices_Center[i][-1]], 0, (0,0,255), 2)
            # # cv2.drawContours(demo_draw, [self.ContourSlices_Center[i][0]], 0, (0,255,0), 2)
            # cv2.drawContours(demo_draw, [max(contours, key = cv2.contourArea)], 0, (0,0,255), 2)
            # cv2.imshow("Demodraw", demo_draw)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows() 

        """GIỚI HẠN CHO CAMERA BÊN TRÁI"""
        maskLimt = self.Slices_Left[self.NumSlice_LimitLeft-1]
        contours, _ = cv2.findContours(maskLimt, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.Contour_LimitLeft = max(contours, key = cv2.contourArea)

        # demo_draw = self.Faces_Crop_Left[2].copy()
        # cv2.drawContours(demo_draw, [max(contours, key = cv2.contourArea)], 0, (0,0,255), 2)
        # cv2.imshow("Demodraw", demo_draw)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows() 

        """GIỚI HẠN CHO CAMERA BÊN PHẢI"""
        maskLimt = self.Slices_Right[self.NumSlice_LimitRight-1]
        contours, _ = cv2.findContours(maskLimt, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.Contour_LimitRight = max(contours, key = cv2.contourArea)

        # demo_draw = self.Face_Crop_Right.copy()
        # cv2.drawContours(demo_draw, [max(contours, key = cv2.contourArea)], 0, (0,0,255), 2)
        # cv2.imshow("Demodraw", demo_draw)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows() 

    """TÍNH HỆ SỐ DIỆN TÍCH CHO LÁT CẮT"""
    def ConstAreaSlices(self):
        self.ConstSlices_Center = []
        self.ConstSlices_Left = []
        self.ConstSlices_Right = []

        """HỆ SỐ DIỆN TÍCH CHO LÁT CẮT Ở CAMERA GIỮA"""
        for i in range (4):
            ConstSlices_Center = []
            for height in self.SliceHeight_CenterFaces[i]:
                ConstSlices_Center.append(self.Func_ConstArea_Center[0]*height+self.Func_ConstArea_Center[1])
            self.ConstSlices_Center.append(ConstSlices_Center)
        # print(self.ConstSlices_Center)

        """HỆ SỐ DIỆN TÍCH CHO LÁT CẮT Ở CAMERA BÊN TRÁI"""
        for height in self.SliceHeight_LeftFace:
            self.ConstSlices_Left.append(self.Func_ConstArea_Left[0]*height+self.Func_ConstArea_Left[1])
        # print("height_left", min(self.SliceHeight_LeftFace), max(self.SliceHeight_LeftFace))
        # print(self.ConstSlices_Left)

        """HỆ SỐ DIỆN TÍCH CHO LÁT CẮT Ỏ CAMERA BÊN PHẢI"""
        for height in self.SliceHeight_RightFace:
            self.ConstSlices_Right.append(self.Func_ConstArea_Right[0]*height+self.Func_ConstArea_Right[1])
        # print("height_right", min(self.SliceHeight_RightFace), max(self.SliceHeight_RightFace))
        # print(self.ConstSlices_Right)            

    """TÌM VÀ TÍNH DIỆN TÍCH KHUYẾT ĐIỂM"""
    def FindDefect(self):
        def Defect_Area(defect, slices, intensity, const, scaleface):
            defArea = 0
            for i in range(len(slices)):
                idx = int((intensity[i] - min(intensity)) / min(intensity))
                defArea += np.count_nonzero(np.abs(defect-(intensity[i]))<2) * (1/((scaleface)**2)) * const[idx]
            return defArea

        """TÍNH DIỆN TÍCH KHUYẾT ĐIỂM CHO CAMERA BÊN TRÁI"""
        Defects_Contour_Left, mask_Defect_Left = Mod.find_DefectContours(face=self.Faces_Crop_Left[2], 
                                                                         maskMango=self.Masks_Mango_Left[2],
                                                                         cordinate_Box=self.Cordinate_BoxLeft[0],
                                                                         plotsmall=False, plotbig=False, tape = self.Tape)

        self.All_Defects_Left = np.ones((self.SizeCrop_Left[2][1], self.SizeCrop_Left[2][0]), np.uint8)
        self.Slice_Defects_left = []
        self.Areas_Left = []
        for cnt in Defects_Contour_Left:
            # cv2.drawContours(self.Faces_Crop_Left[2], [cnt], -1, (0, 0, 255), 1)
            '''xác định tâm khuyết điểm'''
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX = int(cnt[0][0][0])
                cY = int(cnt[0][0][1])
            '''kiểm tra tâm khuyết điểm với đường viền giới hạn'''
            check = cv2.pointPolygonTest(self.Contour_LimitLeft, (cX, cY), True)
            # check = cv2.pointPolygonTest(self.ContourSlices_Left[0], (cX, cY), True)
            '''tính diện tích khuyết điểm'''
            if check>=0 and self.minArea<=cv2.contourArea(cnt)<self.maxArea:
                command = None
                if self.CheckTape[0]==1 and self.Tape is True:
                    demodraw = self.Faces_Crop_Left[2].copy()
                    cv2.drawContours(demodraw, [cnt], -1, (0, 0, 255), 2)
                    cv2.imshow("demmodraw", demodraw)
                    key = cv2.waitKey(1)
                    command = input("Type y if correct: ")
                
                if command is None or command == "y":
                    cv2.drawContours(self.Faces_Crop_Left[2], [cnt], -1, (0, 0, 255), 1)
                    width, height = self.SizeCrop_Left[2]
                    defect = np.zeros((height, width), dtype = np.uint8)
                    cv2.drawContours(defect, [cnt], -1, 255, -1)
                    slDefect = cv2.bitwise_and(defect, self.SlicedFace_Left)
                    if cv2.countNonZero(slDefect) > 0:
                        self.Slice_Defects_left.append(slDefect)
                        self.All_Defects_Left = cv2.bitwise_or(self.All_Defects_Left, slDefect)
                    area = Defect_Area(defect=slDefect, 
                                        slices=self.Slices_Left,
                                        intensity=self.Intensity_Left,
                                        const=self.ConstSlices_Left,
                                        scaleface=self.Scale_Left)
                    # angle_0, angle_1 = self.AngleDefect_Left(cX, cY)
                    # area =  area*(np.sqrt(1+(np.tan(angle_0))**2+(np.tan(angle_1))**2))
                    self.Areas_Left.append(area)
                    self.AllArea.append(area)

                    if self.Tape:
                        cv2.putText(self.Faces_Crop_Left[2], str(round(area,2)), (cX - 7, cY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_8)
        if self.Tape is False:
            cv2.putText(self.Faces_Crop_Left[2], str(round(sum(self.Areas_Left),2))+"mm2",(10, self.SizeCrop_Left[2][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_8)
        # cv2.imshow("defect left", self.Faces_Crop_Left[2])

        """TÍNH DIỆN TÍCH KHUYẾT ĐIỂM CHO CAMERA BÊN PHẢI"""
        Defects_Contour_Right, mask_Defect_Right = Mod.find_DefectContours(face=self.Face_Crop_Right, 
                                                                           maskMango=self.Mask_Mango_Right,
                                                                           cordinate_Box=self.Cordinate_BoxRight[0],
                                                                           plotsmall=False, plotbig=False, tape = self.Tape)
        width, height = self.SizeCrop_Right
        self.All_Defects_Right = np.ones((height, width), np.uint8)
        self.Slice_Defects_Right = []
        self.Areas_Right = []
        for cnt in Defects_Contour_Right:
            # cv2.drawContours(self.Face_Crop_Right, [cnt], -1, (0, 0, 255), 1)
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX = int(cnt[0][0][0])
                cY = int(cnt[0][0][1])
            check = cv2.pointPolygonTest(self.Contour_LimitRight, (cX, cY), True)
            # check = cv2.pointPolygonTest(self.ContourSlices_Right[0], (cX, cY), True) 
            if check>=0 and self.minArea<=cv2.contourArea(cnt)<self.maxArea:
                command = None
                if self.CheckTape[1]==1 and self.Tape is True:
                    demodraw = self.Face_Crop_Right.copy()
                    cv2.drawContours(demodraw, [cnt], -1, (0, 0, 255), 2)
                    cv2.imshow("demmodraw", demodraw)
                    key = cv2.waitKey(1)
                    command = input("Type y if correct: ")
                
                if command is None or command == "y":
                    cv2.drawContours(self.Face_Crop_Right, [cnt], -1, (0, 0, 255), 1)
                    defect = np.zeros((height, width), dtype = np.uint8)
                    cv2.drawContours(defect, [cnt], -1, 255, -1)
                    slDefect = cv2.bitwise_and(defect, self.SlicedFace_Right)
                    if cv2.countNonZero(slDefect) > 0:
                        self.Slice_Defects_Right.append(slDefect)
                        self.All_Defects_Right = cv2.bitwise_or(self.All_Defects_Right, slDefect)
                    area = Defect_Area(defect=slDefect, 
                                        slices=self.Slices_Right,
                                        intensity=self.Intensity_Right,
                                        const=self.ConstSlices_Right,
                                        scaleface=self.Scale_Right) 
                    # angle_0, angle_1 = self.AngleDefect_Right(cX, cY)
                    # area =  area*(np.sqrt(1+(np.tan(angle_0))**2+(np.tan(angle_1))**2))
                    self.Areas_Right.append(area)
                    self.AllArea.append(area)
                    if self.Tape:
                        cv2.putText(self.Face_Crop_Right, str(round(area,2)), (cX - 7, cY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_8)
        if self.Tape is False:
            cv2.putText(self.Face_Crop_Right, str(round(sum(self.Areas_Right),2))+"mm2", ((10, self.SizeCrop_Right[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_8)      
        
        if self.NumSlice_Left == self.NumSlice_Tail and (self.CheckTape[0]==1 or self.CheckTape[1]==0) and self.Tape is True:
            temp = self.AllArea[0]
            self.AllArea[0] = self.AllArea[1]
            self.AllArea[1] = temp
        
        """#TÍNH DIỆN TÍCH KHUYẾT ĐIỂM CHO CAMERA Ở GIỮA"""
        self.All_Defects_Center = []
        self.Slice_Defects_Center = []
        self.Areas_Center = []
        for i in range(4):
            Areas = []
            # if i==2:
            #     plotbig = True
            #     plotsmall = True
            #     # demo = self.Faces_Crop_Center[i].copy()
            #     # for cor in self.Cordinate_BoxCenter[i]:
            #     #     cv2.rectangle(demo, cor[0], cor[1], (0,255,0), 1)
            #     # cv2.imshow('face', self.Faces_Crop_Center[i])
            #     # cv2.imshow('demo', demo)
            #     # cv2.waitKey(0)
            # else:
            #     plotbig = False
            #     plotsmall = False
            Defects_Contour_Center, mask_Defect_Center = Mod.find_DefectContours(face=self.Faces_Crop_Center[i], 
                                                                                 maskMango=self.Masks_RMstem_Center[i],
                                                                                 cordinate_Box=self.Cordinate_BoxCenter[i],
                                                                                 plotsmall=False, plotbig=False, tape = self.Tape)
            # cv2.imshow("0", mask_Defect_Center)
            # demo = self.Faces_Crop_Center[i].copy()
            # for df in Defects_Contour_Center:
            #     cv2.drawContours(demo, [df], 0, (0,255,0), 1)
            # cv2.imshow("1", demo)
            # cv2.waitKey(0)
            
            allDefects_center = np.zeros((self.SizeCrop_Center[i][1], self.SizeCrop_Center[i][0]), np.uint8)
            slice_Defects_center = []
            
            # demodraw = self.SlicedFace_Center[i].copy()
            # demodraw = cv2.cvtColor(demodraw, cv2.COLOR_GRAY2BGR)
            # blank = np.zeros_like(allDefects_center)

            for cnt in Defects_Contour_Center:
                # cv2.drawContours(self.Faces_Crop_Center[i], [cnt], -1, (0, 0, 255), 1)
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                else:
                    cX = int(cnt[0][0][0])
                    cY = int(cnt[0][0][1])
                check = cv2.pointPolygonTest(self.Contour_LimitCenter[i], (cX, cY), True)
                # check = cv2.pointPolygonTest(self.ContourSlices_Center[i][0], (cX, cY), True) 
                # if 110<cv2.contourArea(cnt)<400 and check>=0:
                if check>=0 and self.minArea<=cv2.contourArea(cnt)<self.maxArea:
                    command = None
                    if self.CheckTape[2]==1 and self.Tape is True:
                        demodraw = self.Faces_Crop_Center[i].copy()
                        cv2.drawContours(demodraw, [cnt], -1, (0, 0, 255), 2)
                        cv2.imshow("Demmodraw", demodraw)
                        key = cv2.waitKey(1)
                        command = input("Type y if correct: ")
                    
                    if command is None or command == "y":
                        cv2.drawContours(self.Faces_Crop_Center[i], [cnt], -1, (0, 0, 255), 1)
                        width, height = self.SizeCrop_Center[i]
                        defect = np.zeros((height, width), dtype = np.uint8)
                        cv2.drawContours(defect, [cnt], 0, 255, -1)
                        slDefect = cv2.bitwise_and(self.SlicedFace_Center[i], defect)
                        if cv2.countNonZero(slDefect) > 0:
                            slice_Defects_center.append(slDefect)
                            allDefects_center = cv2.bitwise_or(allDefects_center, slDefect)
                        area = Defect_Area(defect=slDefect, 
                                        slices=self.Slices_Center[i],
                                        intensity=self.Intensity_Center[i],
                                        const=self.ConstSlices_Center[i],
                                        scaleface=self.Scale_Center)

                        angle_0, angle_1 = self.AngleDefect_Center(numface=i, x_cordinate=cX, y_cordinate=cY)
                        area =  area*(np.sqrt(1+(np.tan(angle_0))**2+(np.tan(angle_1))**2))
                        # cv2.imshow("sliceonDF", self.Slices_Center[anotherFce][numslicenearest])
                        # cv2.imshow("deff", self.Faces_Crop_Center[i])
                        # cv2.waitKey(0)
                        Areas.append(area)
                        self.AllArea.append(area)
                        self.Areas_Center.append(area)
                        if self.Tape:
                            cv2.putText(self.Faces_Crop_Center[i], str(round(area,2)), (cX - 7, cY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_8)
            if self.Tape is False:
                cv2.putText(self.Faces_Crop_Center[i], str(round(sum(Areas),2))+"mm2", ((10, self.SizeCrop_Center[i][1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_8)      
            # self.All_Defects_Center.append(allDefects_center)
            # self.Slice_Defects_Center.append(slice_Defects_center)
            # cv2.imshow("demodraw2", demodraw)
            # cv2.imshow("Slices", allDefects_center)
            # cv2.imshow("blank", blank)
            # cv2.waitKey(0)
             
    """TÌM GÓC NGHIÊNG CỦA KHUYẾT ĐIỂM TRÊN MẶT XOÀI CHỤP TỪ CAMERA 1"""
    def AngleDefect_Center(self, numface, x_cordinate, y_cordinate):
        """TÌM GÓC NGHIÊNG THEO HƯỚNG 1"""
        if y_cordinate <=self.Intersection_Center[numface][1]:
            mode = "Bottom"
            back_cY = y_cordinate
            if numface==0:
                anotherFace = 3
            elif numface==3:
                anotherFace = 2
            else:
                anotherFace = numface-1
        else:
            back_cY = self.SizeCrop_Center[numface][1]-y_cordinate
            mode = "Top"
            if numface==0:
                anotherFace = 1
            elif numface==3:
                anotherFace = 0
            else:
                anotherFace = numface+1

        slice_nearest = None
        min_difference = float('inf')    
        for k in range (len(self.ContourSlices_Center[anotherFace])):
            difference = np.abs(self.SlicePoint_CenterFaces[anotherFace][k][0][1]-back_cY)
            if difference < min_difference:
                min_difference = difference
                slice_nearest = k  

        slice_contour = self.ContourSlices_Center[anotherFace][slice_nearest]            
        x_OnAnotherFce = self.SizeCrop_Center[anotherFace][0]*(x_cordinate/self.SizeCrop_Center[numface][0])
        contourCrop, pointOnContour = Mod.cutContour(value=x_OnAnotherFce, border=self.Intersection_Center[anotherFace][1],
                                                     contour=slice_contour, mode=mode)
        angle_0, [vx, vy, x, y] = Mod.findAngle(contourCrop=contourCrop, axis=0)

        # demodraw_1 = self.Faces_Crop_Center[anotherFace].copy()
        # rows,cols = demodraw_1.shape[:2]
        # lefty = int((-x*vy/vx) + y)
        # righty = int(((cols-x)*vy/vx)+y) 
        # # cv2.drawContours(demodraw_1,[slice_contour], 0, (255,0,0), 2)
        # cv2.line(demodraw_1,(cols-1,righty),(0,lefty),(0,255,0),1) 
        # cv2.drawContours(demodraw_1,[contourCrop], 0, (0,0,255), 2)
        # cv2.circle(img = demodraw_1, center = (int(pointOnContour[0]),int(pointOnContour[1])), radius=3, color=(255, 0, 0), thickness=-1)
        # cv2.imshow("demodraw 1", demodraw_1)
        # # cv2.imshow("curentFce", self.Faces_Crop_Center[numface])
        # cv2.waitKey(0)

        """TÌM GÓC NGHIÊNG THEO HƯỚNG 2"""
        if x_cordinate<=self.Intersection_Center[numface][0]:
            slice_nearest = None
            min_difference = float('inf')
            for k in range (len(self.ContourSlices_Left)):
                difference = np.abs(self.SlicePoint_LeftFaces[k][0][0]-x_cordinate)
                if difference < min_difference:
                    min_difference = difference
                    slice_nearest = k 
            slice_contour = self.ContourSlices_Left[slice_nearest]                   
            if numface == 0:
                mode = "Bottom"
                y_OnAnotherFce = self.SizeCrop_Left[2][0]*((self.SizeCrop_Center[numface][1]-y_cordinate)/self.SizeCrop_Center[numface][1])
                border=self.Intersection_Left[2][1]
                axis = 0
            elif numface == 1:
                mode = "Left"
                y_OnAnotherFce = self.SizeCrop_Left[2][1]*((self.SizeCrop_Center[numface][1]-y_cordinate)/self.SizeCrop_Center[numface][1])
                border=self.Intersection_Left[2][0]
                axis = 1
            elif numface == 2:
                mode = "Top"
                y_OnAnotherFce = self.SizeCrop_Left[2][0]*(y_cordinate/self.SizeCrop_Center[numface][1])
                border=self.Intersection_Left[2][1]
                axis = 0
            else:
                mode = "Right"
                y_OnAnotherFce = self.SizeCrop_Left[2][1]*(y_cordinate/self.SizeCrop_Center[numface][1])
                border=self.Intersection_Left[2][0]
                axis = 1

            contourCrop, pointOnContour = Mod.cutContour(value=y_OnAnotherFce, border=border,
                                                         contour=slice_contour, mode=mode)
            angle_1, [vx, vy, x, y] = Mod.findAngle(contourCrop=contourCrop, axis=axis)

            # demodraw_1 = self.Faces_Crop_Left[2].copy()
            # rows,cols = demodraw_1.shape[:2]
            # lefty = int((-x*vy/vx) + y)
            # righty = int(((cols-x)*vy/vx)+y)
            # # cv2.drawContours(demodraw_1,[slice_contour], 0, (255,0,0), 2)
            # cv2.line(demodraw_1,(cols-1,righty),(0,lefty),(0,255,0),1)
            # cv2.drawContours(demodraw_1,[contourCrop], 0, (0,0,255), 2)
            # cv2.circle(img = demodraw_1, center = (int(pointOnContour[0]),int(pointOnContour[1])), radius=3, color=(255, 0, 0), thickness=-1)
            # cv2.imshow("demodraw 1", demodraw_1)
            # # cv2.imshow("curentFce", self.Faces_Crop_Center[numface])
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()     
        else:
            slice_nearest = None
            min_difference = float('inf')
            for k in range (len(self.ContourSlices_Right)):
                difference = np.abs(self.SlicePoint_RightFaces[k][0][0]-x_cordinate)
                if difference < min_difference:
                    min_difference = difference
                    slice_nearest = k

            slice_contour = self.ContourSlices_Right[slice_nearest]
            if numface == 0:
                mode = "Bottom"
                y_OnAnotherFce = self.SizeCrop_Right[0]*(y_cordinate/self.SizeCrop_Center[numface][1])
                axis = 0
                border = self.Intersection_Right[1]
            if numface == 1:
                mode = "Right"
                y_OnAnotherFce = self.SizeCrop_Right[1]*((self.SizeCrop_Center[numface][1]-y_cordinate)/self.SizeCrop_Center[numface][1])
                axis = 1
                border = self.Intersection_Right[0]
            if numface == 2:
                mode = "Top"
                y_OnAnotherFce = self.SizeCrop_Right[0]*((self.SizeCrop_Center[numface][1]-y_cordinate)/self.SizeCrop_Center[numface][1])
                axis = 0
                border = self.Intersection_Right[1]
            if numface == 3:
                mode = "Left"
                y_OnAnotherFce = self.SizeCrop_Right[1]*(y_cordinate/self.SizeCrop_Center[numface][1])
                axis = 1
                border = self.Intersection_Right[0]

            contourCrop, pointOnContour = Mod.cutContour(value=y_OnAnotherFce, border=border,
                                                         contour=slice_contour, mode=mode)
            angle_1, [vx, vy, x, y] = Mod.findAngle(contourCrop=contourCrop, axis=axis)

            # demodraw_1 = self.Face_Crop_Right.copy()
            # rows,cols = demodraw_1.shape[:2]
            # lefty = int((-x*vy/vx) + y)
            # righty = int(((cols-x)*vy/vx)+y)
            # # cv2.drawContours(demodraw_1,[slice_contour], 0, (255,0,0), 2)
            # cv2.line(demodraw_1,(cols-1,righty),(0,lefty),(0,255,0),1) 
            # cv2.drawContours(demodraw_1,[contourCrop], 0, (0,0,255), 2)
            # cv2.circle(img = demodraw_1, center = (int(pointOnContour[0]),int(pointOnContour[1])), radius=3, color=(255, 0, 0), thickness=-1)
            # cv2.imshow("demodraw 1", demodraw_1)
            # # cv2.imshow("curentFce", self.Faces_Crop_Center[numface])
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

        return angle_0[0], angle_1[0]
    
    """TÌM GÓC NGHIÊNG CỦA KHUYẾT ĐIỂM TRÊN MẶT XOÀI CHỤP TỪ CAMERA 2"""
    def AngleDefect_Left(self, x_cordinate, y_cordinate):
        """TÌM GÓC NGHIÊNG THEO HƯỚNG 1"""
        if y_cordinate <= self.Intersection_Left[2][1]:
            anotherFace = 2
            back_cY = y_cordinate
            x_OnAnotherFce = self.SizeCrop_Center[anotherFace][1]*(x_cordinate/self.SizeCrop_Left[2][0])           
        else:
            anotherFace = 0
            back_cY = self.SizeCrop_Left[2][1]-y_cordinate
            x_OnAnotherFce = self.SizeCrop_Center[anotherFace][1]*((self.SizeCrop_Left[2][0]-x_cordinate)/self.SizeCrop_Left[2][0])

        slice_nearest = None
        min_difference = float('inf')
        for k in range (len(self.ContourSlices_Center[anotherFace])):
            difference = np.abs(self.SlicePoint_CenterFaces[anotherFace][k][0][1]-back_cY)
            if difference < min_difference:
                min_difference = difference
                slice_nearest = k
        slice_contour = self.ContourSlices_Center[anotherFace][slice_nearest] 
        contourCrop, pointOnContour = Mod.cutContour(value = x_OnAnotherFce, border=self.Intersection_Center[anotherFace][0],
                                                        contour=slice_contour, mode='Left') 
        angle_0, [vx, vy, x, y] = Mod.findAngle(contourCrop=contourCrop, axis=1)

        # demodraw_1 = self.Faces_Crop_Center[anotherFace].copy()
        # rows,cols = demodraw_1.shape[:2]
        # lefty = int((-x*vy/vx) + y)
        # righty = int(((cols-x)*vy/vx)+y)
        # cv2.drawContours(demodraw_1,[slice_contour], 0, (255,0,0), 2)
        # cv2.line(demodraw_1,(cols-1,righty),(0,lefty),(0,255,0),2)  
        # cv2.circle(img = demodraw_1, center = (int(pointOnContour[0]),int(pointOnContour[1])), radius=4, color=(0, 0, 255), thickness=-1)
        # cv2.drawContours(demodraw_1,[contourCrop], 0, (0,255,0), 2)
        # cv2.imshow("demodraw 1", demodraw_1)
        # cv2.imshow("curentFce", self.Faces_Crop_Left[2])
        # cv2.waitKey(0)

        """TÌM GÓC NGHIÊNG THEO HƯỚNG 2"""
        if x_cordinate >= self.Intersection_Left[2][0]:
            anotherFace = 3
            back_cX = self.SizeCrop_Left[2][0]-x_cordinate
            y_OnAnotherFce = self.SizeCrop_Center[anotherFace][1]*(y_cordinate/self.SizeCrop_Left[2][1])
        else:
            anotherFace = 1
            back_cX = x_cordinate 
            y_OnAnotherFce = self.SizeCrop_Center[anotherFace][1]*((self.SizeCrop_Left[2][1]-y_cordinate)/self.SizeCrop_Left[2][1])

        slice_nearest = None
        min_difference = float('inf')
        for k in range (len(self.ContourSlices_Center[anotherFace])):
            difference = np.abs(self.SlicePoint_CenterFaces[anotherFace][k][0][1]-back_cX)
            if difference < min_difference:
                min_difference = difference
                slice_nearest = k
        slice_contour = self.ContourSlices_Center[anotherFace][slice_nearest]
        contourCrop, pointOnContour = Mod.cutContour(value = y_OnAnotherFce, border=self.Intersection_Center[anotherFace][0],
                                                        contour=slice_contour, mode='Left')
        angle_1, [vx, vy, x, y] = Mod.findAngle(contourCrop=contourCrop, axis=1)
        
        # demodraw_1 = self.Faces_Crop_Center[anotherFace].copy()
        # rows,cols = demodraw_1.shape[:2]
        # lefty = int((-x*vy/vx) + y)
        # righty = int(((cols-x)*vy/vx)+y)
        # cv2.drawContours(demodraw_1,[slice_contour], 0, (255,0,0), 2)
        # cv2.line(demodraw_1,(cols-1,righty),(0,lefty),(0,255,0),2)  
        # cv2.circle(img = demodraw_1, center = (int(pointOnContour[0]),int(pointOnContour[1])), radius=4, color=(0, 0, 255), thickness=-1)
        # cv2.drawContours(demodraw_1,[contourCrop], 0, (0,255,0), 2)
        # cv2.imshow("demodraw 1", demodraw_1)
        # cv2.imshow("curentFce", self.Faces_Crop_Left[2])
        # cv2.waitKey(0)

        return angle_0[0], angle_1[0]

    """TÌM GÓC NGHIÊNG CỦA KHUYẾT ĐIỂM TRÊN MẶT XOÀI CHỤP TỪ CAMERA 3"""
    def AngleDefect_Right(self, x_cordinate, y_cordinate):
        """TÌM GÓC NGHIÊNG THEO HƯỚNG 1"""
        if y_cordinate <= self.Intersection_Right[1]:
            anotherFace = 2
            back_cY = y_cordinate
            x_OnAnotherFce = self.SizeCrop_Center[anotherFace][1]*((self.SizeCrop_Right[0]-x_cordinate)/self.SizeCrop_Right[0])
        else:
            anotherFace = 0
            back_cY = self.SizeCrop_Right[1]-y_cordinate
            x_OnAnotherFce = self.SizeCrop_Center[anotherFace][1]*(x_cordinate/self.SizeCrop_Right[0])

        slice_nearest = None
        min_difference = float('inf')
        for k in range (len(self.ContourSlices_Center[anotherFace])):
            difference = np.abs(self.SlicePoint_CenterFaces[anotherFace][k][0][1]-back_cY)
            if difference < min_difference:
                min_difference = difference
                slice_nearest = k
        slice_contour = self.ContourSlices_Center[anotherFace][slice_nearest]
        contourCrop, pointOnContour = Mod.cutContour(value = x_OnAnotherFce, border=self.Intersection_Center[anotherFace][0],
                                                        contour=slice_contour, mode='Right')

        angle_0, [vx, vy, x, y] = Mod.findAngle(contourCrop=contourCrop, axis=1)

        # demodraw_1 = self.Faces_Crop_Center[anotherFace].copy()
        # rows,cols = demodraw_1.shape[:2]
        # lefty = int((-x*vy/vx) + y)
        # righty = int(((cols-x)*vy/vx)+y)
        # cv2.drawContours(demodraw_1,[slice_contour], 0, (255,0,0), 2)
        # cv2.line(demodraw_1,(cols-1,righty),(0,lefty),(0,255,0),2) 
        # cv2.circle(img = demodraw_1, center = (int(pointOnContour[0]),int(pointOnContour[1])), radius=4, color=(0, 0, 255), thickness=-1)
        # cv2.drawContours(demodraw_1,[contourCrop], 0, (0,255,0), 2)
        # cv2.imshow("demodraw 1", demodraw_1)
        # cv2.imshow("curentFce", self.Face_Crop_Right)
        # cv2.waitKey(0) 
        
        """TÌM GÓC NGHIÊNG THEO HƯỚNG 2"""
        if x_cordinate>=self.Intersection_Right[0]:
            anotherFace = 1
            back_cX = self.SizeCrop_Right[0]-x_cordinate
            y_OnAnotherFce = self.SizeCrop_Center[anotherFace][1]*((self.SizeCrop_Right[1]-y_cordinate)/self.SizeCrop_Right[1])
        else:
            anotherFace = 3
            back_cX = x_cordinate
            y_OnAnotherFce = self.SizeCrop_Center[anotherFace][1]*(y_cordinate/self.SizeCrop_Right[1])

        slice_nearest = None
        min_difference = float('inf')
        for k in range (len(self.ContourSlices_Center[anotherFace])):
            difference = np.abs(self.SlicePoint_CenterFaces[anotherFace][k][0][1]-back_cX)
            if difference < min_difference:
                min_difference = difference
                slice_nearest = k

        slice_contour = self.ContourSlices_Center[anotherFace][slice_nearest]
        contourCrop, pointOnContour = Mod.cutContour(value = y_OnAnotherFce, border=self.Intersection_Center[anotherFace][0],
                                                        contour=slice_contour, mode='Right')
        angle_1, [vx, vy, x, y] = Mod.findAngle(contourCrop=contourCrop, axis=1)

        # demodraw_1 = self.Faces_Crop_Center[anotherFace].copy()
        # rows,cols = demodraw_1.shape[:2]
        # lefty = int((-x*vy/vx) + y)
        # righty = int(((cols-x)*vy/vx)+y)
        # cv2.drawContours(demodraw_1,[slice_contour], 0, (255,0,0), 2)
        # cv2.line(demodraw_1,(cols-1,righty),(0,lefty),(0,255,0),2) 
        # cv2.circle(img = demodraw_1, center = (int(pointOnContour[0]),int(pointOnContour[1])), radius=4, color=(0, 0, 255), thickness=-1)
        # cv2.drawContours(demodraw_1,[contourCrop], 0, (0,255,0), 2)
        # cv2.imshow("demodraw 1", demodraw_1)
        # cv2.imshow("curentFce", self.Face_Crop_Right)
        # cv2.waitKey(0)

        return angle_0[0], angle_1[0]        

        
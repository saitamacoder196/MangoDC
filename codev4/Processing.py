import cv2
import pandas as pd
from myLib.ImageProcess import Processing
from myLib import Module as Mod
from datetime import datetime
import csv
import os, re
import numpy as np

"""Đường dẫn đến thư lục hình"""
# imagefolder = "Image Mango/No Tape/Final_24.1.9-24.1.17"
# imagefolder = "Image Mango/No Tape/24.1.9-Catchu"
imagefolder = "Image Mango/Tape/Final_24.1.9-24.1.17"
# imagefolder = "Image Mango/Tape/24.1.9-Catchu"
filenames = os.listdir(imagefolder)
sorted_filenames = sorted(filenames, key=lambda x: tuple(map(int, re.findall(r'\d+', x))))

"""Đưỡng dẫn đến file csv diện tích khuyết điểm giả định"""
# csvfile = "Check Accuracy/Areas_CC.csv"
csvfile = "Check Accuracy/Areas_HL.csv"
df = pd.read_csv(csvfile)
"""Kiểm tra từng khuyết điểm trên bề mặt (Dùng cho xoài dán khuyết điểm giả định) 
Phần tử 1: 1: kiểm tra/ 0: không kiểm tra khuyết điểm camera 2
Phần tử 2: 1: kiểm tra/ 0: không kiểm tra khuyết điểm camera 3
Phần tử 3: 1: kiểm tra/ 0: không kiểm tra khuyết điểm camera 1
"""
CheckTape = [0,0,0]
save = False #True nếu cần lưu giá trị diện tích khuyết điểm giả định

i = 0 #Số thứ tự quả xoài (chương trình sẽ bắt đầu chạy từ quả xoài có số thứ tự này)
center = []
left = []
right = []
for filename in sorted_filenames:
    name, ext = os.path.splitext(filename)
    parts = name.split("_")
    IDFace = int(parts[1])
    IDMango = int(parts[0].split("-")[0])
    typeFace = parts[0].split("-")[1]

    if IDMango == i:
        if save is True and (i == 1 or i == 2 or i == 6 or i == 10 or i == 11): 
            CheckTape=[1,1,0]
        else: 
            CheckTape=[0,0,0]

        source_path = os.path.join(imagefolder, filename)
        if typeFace=="Center":
            center.append(cv2.imread(source_path))
        elif typeFace == "Left":
            left.append(cv2.imread(source_path))
        elif typeFace == "Right":
            right.append(cv2.imread(source_path))

        if len(center)==4 and len(left)==4 and len(right)==1:
            print("ID mango: ",IDMango)
            Data = Processing(Center_Images=center, Scale_Center=0.5*0.56, 
                            Left_Images=left, Scale_Left=0.5*0.69,
                            Right_Image=right[0], Scale_Right=0.5,
                            Offset=10,NumSlice_Center=12, NumSlice_Head=12, NumSlice_Tail=17,
                            Box_Center=[21,15], Box_LeftRight=[15,14],
                            Func_ConstArea_Center=[5.593593023255808e-06 , 0.007515017476744188],
                            Func_ConstArea_Left=[1.9089044265593567e-05 , -0.0028447316680080513], 
                            Func_ConstArea_Right=[-1.996435199999999e-05 , 0.058740052719999984],
                            Tape = False, CheckTape = CheckTape)
            
            SL_0 = Mod.stackImages([Data.SlicedFace_Left, Data.SlicedFace_Center[0], Data.SlicedFace_Center[2]], 0)
            SL_1 = Mod.stackImages([Data.SlicedFace_Right, Data.SlicedFace_Center[1], Data.SlicedFace_Center[3]], 0)
            SL = Mod.stackImages([SL_0, SL_1], 1)
            SL = cv2.cvtColor(SL, cv2.COLOR_GRAY2BGR)

            RS_0 = Mod.stackImages([Data.Faces_Crop_Left[2],Data.Faces_Crop_Center[0],Data.Faces_Crop_Center[2]], 0)
            RS_1 = Mod.stackImages([Data.Face_Crop_Right,Data.Faces_Crop_Center[1],Data.Faces_Crop_Center[3]], 0)
            RS = Mod.stackImages([RS_0, RS_1], 1)

            FL = Mod.stackImages([SL, RS], 1)

            """Add data"""
            if save is True:
                Data2Add = Data.AllArea
                Data2Add.insert(0, IDMango)
                df.loc[len(df)] = Data2Add

            winname = 'FL_'+str(i)
            cv2.namedWindow(winname) 
            cv2.moveWindow(winname, 0,0)
            cv2.imshow(winname, FL)

            key = cv2.waitKey(20)

            if key == ord('x'):
                cv2.destroyAllWindows()
                break
            else:
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            """Chuyển sang trái tiếp theo"""
            i += 1
            center = []
            left = []
            right = []

"""Lưu diện tích vào file csv"""
if save is True:
    df.to_csv(csvfile, index=False)
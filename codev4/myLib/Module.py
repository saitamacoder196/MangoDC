import numpy as np
import cv2
from matplotlib import pyplot as plt
import matplotlib
from scipy.ndimage import gaussian_filter

pi = 3.14159265

"""THU NHỎ ẢNH
INPUT: Ảnh, tỷ lệ thu nhỏ ảnh
OUTPUT: Ảnh quả xoài đã được thu nhỏ
"""
def Scale(img, ratio):
    h, w = img.shape[:2]# lấy kích thước ảnh hiện tại (h: chiều cao, w chiều ngang)
    '''tỷ lệ cạnh sau khi thu nhỏ'''
    scaledH = int(h * ratio)
    scaledW = int(w * ratio)
    dim = (scaledW, scaledH)
    res = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)#thay đổi kích thước ảnh
    return res

"""TÌM ẢNH NHỊ PHÂN MẶT XOÀI ĐƯỢC CHỤP TỪ CAMERA 1
INPUT: face: mặt quả xoài được chụp từ camera 1
OUTPUT: ảnh nhị phân mặt xoài còn cuốn, ảnh nhị phân mặt xoài đã loại bỏ cuốn
"""
def get_CenterMask(face):
    '''Tìm ảnh nhị phân quả xoài KHÔNG CHỨA KHUYẾT ĐIỂM (CÒN NHIỄU XUNG QUANH QUẢ XOÀI)'''
    h, w = face.shape[:2]#lấy kích thước ảnh
    # cv2.imshow("Anh goc", face) 
    face = cv2.blur(face, (7,7), cv2.BORDER_WRAP)#khử nhiễu
    # cv2.imshow("Khu nhieu", face)  
    frame_LAB = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)#chuyển sang hệ màu Lab
    # cv2.imshow("Anh Lab", frame_LAB)
    binary = cv2.inRange(frame_LAB, (0, 0, 140), (255, 255, 255))#Lấy ngưỡng    
    # cv2.imshow("Loc nguong Lab", binary)

    '''Tìm ảnh nhị phân khuyết điểm (CÒN NHIỄU XUNG QUANH QUẢ XOÀI)'''
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)#Chuyển sang ảnh xám
    # cv2.imshow("Anh xam", gray)
    blank = np.zeros(gray.shape, dtype=np.uint8)#Tạo nền đen
    # cv2.imshow("Tao anh den", blank)
    blank[np.where((gray < 90))] = [255]#Lọc ngưỡng
    # cv2.imshow("loc nguong xam", blank)

    '''Lấp những khuyết điểm ở phần rìa'''
    mask = cv2.bitwise_or(blank, binary)#Cộng ảnh
    # cv2.imshow("Cong anh", mask)

    '''Loại bỏ bớt phần nền (Tự chọn vùng vùng loại bỏ (ĐÃ THỬ NGHIỆM VỚI NHIỀU QUẢ))'''
    blank = np.zeros(gray.shape, dtype=np.uint8)#Tạo nền đen
    # cv2.imshow("Tao anh den moi", blank)
    cv2.rectangle(blank, (int(w/6), int(h/4)), (int(w/10+w*0.83), int(h/4+h*0.51)), 255, -1)#vẽ hình chữ nhật lên nền đen
    # cv2.imshow("Ve hinh chu nhat gioi han len nen den", blank)
    mask = cv2.bitwise_and(mask,blank)#Nhân ảnh 
    # cv2.imshow("Gioi han khung anh", mask)
    
    '''tìm ảnh nhị phân quả xoài (CÒN CUỐN)'''
    mask_Mango = np.zeros(face.shape[:2], dtype=np.uint8)#Tạo nền đen
    # cv2.imshow("Tao nen đen", mask_Mango)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)#Tìm đưỡng viền
    cnt_Mango = max(contours, key=cv2.contourArea)#Xác định đường viền quả xoài (có diện tích lớn nhất)
    cv2.drawContours(mask_Mango, [cnt_Mango], 0, 255, -1)#Vẽ đường viền lên nền đen

    demo = face.copy()
    cv2.drawContours(demo, [cnt_Mango], 0, (0,255,0), 2)
    # cv2.imshow("duong vien lon nhat", demo)
    # cv2.imshow("mask0", mask_Mango)
    # cv2.waitKey(0)

    '''Tìm ảnh nhị phân quả xoài (LOẠI BỎ CUỐN)'''
    rmStemKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50, 50))#Cấu trúc bào mòn (Hình ellipse (trục lớn 50pixels, trục nhỏ 50pixels))
    erode = cv2.erode(mask_Mango, rmStemKernel)#Bào mòn để mất phần cuốn
    # cv2.imshow('bao mon', erode)
    mask_RMstem = cv2.dilate(erode, rmStemKernel)#Phình ra lại để trả về kích thước ban đầu của quả xoài
    # cv2.imshow("gian", mask_RMstem)
    # cv2.waitKey(0)

    return mask_Mango, mask_RMstem

"""TÌM ẢNH NHỊ PHÂN MẶT XOÀI ĐƯỢC CHỤP TỪ CAMERA 2
INPUT: face: mặt quả xoài được chụp từ camera 2
OUTPUT: ảnh nhị phân mặt xoài
"""
def get_LeftMask(face):
    """Test"""
    #     # cv2.imshow("anh goc", face)
    #     filter = cv2.medianBlur(face, 3, cv2.BORDER_WRAP)
    #     # cv2.imshow("khu nhieu", filter)  

    #     frame_LAB = cv2.cvtColor(filter, cv2.COLOR_BGR2LAB)
    #     # cv2.imshow('Anh Lab', frame_LAB)
    #     mask = cv2.inRange(frame_LAB, np.array([0, 0, 152]), np.array([255, 255, 255]))
    #     # cv2.imshow("Nguong Lab", mask)
    #     contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #     contour = max(contours, key = cv2.contourArea)

    #     # demo = face.copy()
    #     # cv2.drawContours(demo, [contour], 0, (0,255,0), 2)
    #     # cv2.imshow("duong vien lon nhat", demo)
    #     # cv2.waitKey(0)

    #     blank = np.zeros_like(mask)
    #     # cv2.imshow("Anh den", blank)
    #     cv2.drawContours(blank, [contour], 0, 255, -1)
    #     # cv2.imshow("Ve duong vien len nen den", blank)
    #     kernel = np.ones((5,5),np.uint8)
    #     erosion = cv2.erode(blank,kernel,iterations = 5)
    #     mask_Mango = cv2.dilate(erosion,kernel,iterations = 5)
    #     # cv2.imshow("bao mon va gian", mask_Mango)
    #     # cv2.waitKey(0)

    #     x,y,w,h = cv2.boundingRect(mask_Mango)
    #     mask_Mango = np.zeros_like(mask_Mango)
    #     cv2.ellipse(mask_Mango, (int(x+w/2), int(y+h/2)), (int(w/2)+2, int(h/2)+2), 0, 0, 360, 255, -1)  

    #     # cv2.imshow("ellipse 0", mask_Mango)


    # cv2.imshow("0", face)
    filter = cv2.medianBlur(face, 3, cv2.BORDER_WRAP)#Khử nhiễu bằng thuật toán medianBlur
    # cv2.imshow("1", filter)
    h, w = face.shape[:2]
    G_GRAY = filter[:,:,1]#Trích kênh Xanh lá (Ảnh xám)
    # cv2.imshow("2", G_GRAY)
    frame_LAB = cv2.cvtColor(filter, cv2.COLOR_BGR2LAB)#Ảnh trong hệ màu RGB
    # cv2.imshow("3", frame_LAB)

    '''TOP'''
    half_TOP = np.zeros((h, w), dtype=np.uint8)#Tạo nền đen
    # cv2.imshow("4", half_TOP)
    cv2.rectangle(half_TOP, (0,0), (w, int(h*(2/3))), 255, -1)#Vẽ hình chữ nhật màu trắng lên nền đen
    # cv2.imshow("5", half_TOP)

    '''Tìm ảnh nhị phân ở phần trên bằng hệ màu Lab'''
    Lab_TOP = cv2.bitwise_and(frame_LAB, frame_LAB, mask = half_TOP)
    # cv2.imshow('6', Lab_TOP)
    mask_a_TOP = cv2.inRange(Lab_TOP, np.array([0, 0, 145]), np.array([255, 255, 255]))
    # cv2.imshow("7", mask_a_TOP)

    '''Tìm ảnh nhị phân ở nửa trên bằng kênh xanh lá'''
    G_TOP = cv2.bitwise_and(G_GRAY, G_GRAY, mask = half_TOP)
    # cv2.imshow("8", G_TOP)
    _,mask_G_TOP = cv2.threshold(G_TOP,130,255,cv2.THRESH_BINARY_INV)
    # cv2.imshow("9", mask_G_TOP)

    '''Tìm ảnh nhị phân ở nửa trên (Cộng ảnh nhị phân Lab và ảnh nhị phân kênh xanh lá)'''
    mask_TOP = cv2.bitwise_or(mask_a_TOP, mask_G_TOP)
    # cv2.imshow('10', mask_TOP)
    mask_TOP = cv2.bitwise_and(mask_TOP, half_TOP)#Loại bỏ phần dưới
    # cv2.imshow('11', mask_TOP)

    '''Tìm đường viền'''
    contours, _ = cv2.findContours(mask_TOP, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mask_TOP = np.zeros_like(mask_TOP)#Tạo nền đen
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 5000<area<40000:#Diện tích quả xoài (Khảo sát trên nhiều trái)
            cv2.drawContours(mask_TOP, [cnt], -1, 255, -1)
            # demo = face.copy()
            # cv2.drawContours(demo, [cnt], 0, (0,255,0), 2)
            # cv2.imshow("12", demo)
            break

    # cv2.imshow("13", mask_TOP)

    '''BOTTOM'''
    filter = cv2.medianBlur(face, 5, cv2.BORDER_WRAP)
    # cv2.imshow("14", filter)

    BOT_Lab = cv2.cvtColor(filter, cv2.COLOR_BGR2LAB)
    # cv2.imshow("15", BOT_Lab)
    G_BOT = filter[:,:,1]
    # cv2.imshow("16", G_BOT)

    '''Loại bỏ nửa trên và hai rulo xoay'''
    half_BOT = np.zeros_like(half_TOP)
    # cv2.imshow("17", half_BOT)
    cv2.rectangle(half_BOT, (120, int(h*2/3)), (w-120, h-76), 255, -1)
    # cv2.imshow("18", half_BOT)
    cv2.circle(half_BOT, (154, 353), 71, 0, -1)
    cv2.circle(half_BOT, (390, 353), 71, 0, -1)
    # cv2.imshow("19", half_BOT)

    '''Tìm ảnh nhị phân phần dưới bằng hệ màu Lab'''
    BOT_Lab = cv2.bitwise_and(BOT_Lab, BOT_Lab,mask = half_BOT)
    # cv2.imshow("20", BOT_Lab)
    mask_Lab = cv2.inRange(BOT_Lab, np.array([0, 0, 155]), np.array([255, 255, 255]))
    # cv2.imshow("21", mask_Lab)

    '''Tìm ảnh nhị phân phần dưới bằng kênh xanh lá'''
    G_BOT = cv2.bitwise_and(G_BOT, half_BOT)
    # cv2.imshow("22", G_BOT)
    _,mask_G_BOT = cv2.threshold(G_BOT,70,255,cv2.THRESH_BINARY_INV)
    # cv2.imshow("23", mask_G_BOT)

    '''Tìm ảnh nhị phân phần dưới (Cộng ảnh nhị phân của hai ảnh vừa tìm)'''
    mask_BOT = cv2.bitwise_or(mask_Lab, mask_G_BOT)
    # cv2.imshow("24", mask_BOT)
    mask_BOT = cv2.bitwise_and(mask_BOT, half_BOT)
    # cv2.imshow("25", mask_BOT)

    '''Tìm đường viền có trong ảnh nhị phân'''
    contours, _ = cv2.findContours(mask_BOT, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mask_BOT = np.zeros_like(mask_BOT)
    cv2.drawContours(mask_BOT, [max(contours, key = cv2.contourArea)], -1, 255, -1)#Vẽ đường viền có diện tích lớn nhất lên nền đen
    
    # demo = face.copy()
    # cv2.drawContours(demo, [max(contours, key = cv2.contourArea)], 0, (0,255,0), 2)
    # cv2.imshow("26", demo)
    # cv2.imshow("27", mask_BOT)

    '''Tìm ảnh nhị phân toàn bộ quả xoài (Cộng ảnh phần trên và phần dưới quả xoài)'''
    mask_Mango = cv2.bitwise_or(mask_BOT, mask_TOP)
    # cv2.imshow("28", mask)

    '''Loại bỏ phần ảnh nhị phân có dạng sợi mỏng'''
    kernel = np.ones((5,5),np.uint8)
    mask_Mango = cv2.erode(mask_Mango,kernel,iterations = 1)
    mask_Mango = cv2.dilate(mask_Mango,kernel,iterations = 1)
    # cv2.imshow("29", mask_Mango)
    # cv2.waitKey(0)

    '''Tìm và vẽ đường viền có diện tich lớn nhất lên nền đen'''
    contours, _ = cv2.findContours(mask_Mango, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mask_Mango = np.zeros_like(mask_Mango)
    cv2.drawContours(mask_Mango, [max(contours, key = cv2.contourArea)], -1, 255, -1)

    x,y,w,h = cv2.boundingRect(mask_Mango)
    mask_Mango = np.zeros_like(mask_Mango)
    cv2.ellipse(mask_Mango, (int(x+w/2), int(y+h/2)), (int(w/2)+2, int(h/2)+2), 0, 0, 360, 255, -1)  
    # cv2.imshow("29", mask_Mango)
    # cv2.waitKey(0)
    
    return mask_Mango

"""TÌM ẢNH NHỊ PHÂN MẶT XOÀI ĐƯỢC CHỤP TỪ CAMERA 3
Đầu vào hàm: face: mặt quả xoài được chụp từ camera 3
OUTPUT: ảnh nhị phân mặt xoài
"""
def get_RightMask(face):
    """Test"""
    #     # cv2.imshow("Anh goc", face) 
    #     filter = cv2.blur(face, (5, 5))
    #     # cv2.imshow("Khu nhieu", filter)  
    #     frame_LAB = cv2.cvtColor(filter, cv2.COLOR_BGR2LAB)
    #     # cv2.imshow("Lab", frame_LAB)  
    #     mask = cv2.inRange(frame_LAB, np.array([0, 0, 137]), np.array([255, 255, 255]))
    #     # cv2.imshow("Anh nhi phan", mask) 
    #     contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #     contour = max(contours, key = cv2.contourArea)

    #     demo = face.copy()
    #     cv2.drawContours(demo, [contour], 0, (0,255,0), 2)
    #     # cv2.imshow("duong vien lon nhat", demo)

    #     blank = np.zeros_like(mask)
    #     cv2.drawContours(blank, [contour], 0, 255, -1)
    #     # cv2.imshow("nhi phan duong vien", blank) 
    #     kernel = np.ones((5,5),np.uint8)
    #     erosion = cv2.erode(blank,kernel,iterations = 5)
    #     mask_Mango = cv2.dilate(erosion,kernel,iterations = 5)
    #     # cv2.imshow("Bao mon, gian", mask_Mango)

    #     x,y,w,h = cv2.boundingRect(mask_Mango)
    #     mask_Mango = np.zeros_like(mask_Mango)
    #     cv2.ellipse(mask_Mango, (int(x+w/2), int(y+h/2)), (int(w/2)+2, int(h/2)+2), 0, 0, 360, 255, -1)  

    #     # cv2.imshow("ellipse", mask_Mango)
    
    """TOP"""
    # cv2.imshow("0", face)
    h, w = face.shape[:2]
    G_GRAY = face[:,:,1]
    # cv2.imshow("1", G_GRAY)
    frame_LAB = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)
    # cv2.imshow("2", frame_LAB)

    half_TOP = np.zeros((h, w), dtype=np.uint8)
    # cv2.imshow('3', half_TOP)
    cv2.rectangle(half_TOP, (0,0), (w, int(h*(0.55))), 255, -1)
    # cv2.imshow('4', half_TOP)

    Lab_TOP = cv2.bitwise_and(frame_LAB, frame_LAB, mask = half_TOP)
    # cv2.imshow('5', Lab_TOP)
    mask_a_TOP = cv2.inRange(Lab_TOP, np.array([0, 0, 135]), np.array([255, 255, 255]))
    # cv2.imshow("6", mask_a_TOP)
    G_TOP = cv2.bitwise_and(G_GRAY, G_GRAY, mask = half_TOP)
    # cv2.imshow('7', G_TOP)
    _,mask_G_TOP = cv2.threshold(G_TOP,120,255,cv2.THRESH_BINARY_INV)
    # cv2.imshow("8", mask_G_TOP)
    mask_TOP = cv2.bitwise_or(mask_a_TOP, mask_G_TOP)
    # cv2.imshow("9", mask_TOP)
    mask_TOP = cv2.bitwise_and(mask_TOP, half_TOP)
    # cv2.imshow("10", mask_TOP)
    
    contours, _ = cv2.findContours(mask_TOP, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mask_TOP = np.zeros_like(mask_TOP)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 5000<area<40000:
            cv2.drawContours(mask_TOP, [cnt], -1, 255, -1)
            # demo = face.copy()
            # cv2.drawContours(demo, [cnt], 0, (0,255,0), 2)
            # cv2.imshow("11", demo)
            break
    # cv2.imshow("12",mask_TOP)

    '''Bottom'''
    # filter = cv2.medianBlur(face, 3, cv2.BORDER_WRAP)
    filter = face
    half_BOT = np.zeros_like(half_TOP)
    # cv2.imshow("13", half_BOT)
    cv2.rectangle(half_BOT, (250, int(h*0.55)), (w-250, h-150), 255, -1)
    # cv2.imshow('14', half_BOT)
    cv2.circle(half_BOT, (370, 450), 71, 0, -1)
    cv2.circle(half_BOT, (600, 450), 71, 0, -1)
    # cv2.imshow('15', half_BOT)

    
    BOT_Lab = cv2.cvtColor(filter, cv2.COLOR_BGR2LAB)
    # cv2.imshow("16", BOT_Lab)
    G_BOT = filter[:,:,1]
    # cv2.imshow("17", G_BOT)
    BOT_Lab = cv2.bitwise_and(BOT_Lab, BOT_Lab, mask = half_BOT)
    # cv2.imshow('18', BOT_Lab)
    G_BOT = cv2.bitwise_and(G_BOT, half_BOT)
    # cv2.imshow('19', G_BOT)

    mask_Lab = cv2.inRange(BOT_Lab, np.array([0, 0, 136]), np.array([255, 255, 255]))
    # cv2.imshow('20',mask_Lab)
    # cv2.waitKey(0)

    _,mask_G_BOT = cv2.threshold(G_BOT,60,255,cv2.THRESH_BINARY_INV)
    # cv2.imshow('21', mask_G_BOT)
    mask_G_BOT = cv2.bitwise_and(mask_G_BOT, half_BOT)
    # cv2.imshow("22", mask_G_BOT)
    mask_BOT = cv2.bitwise_or(mask_Lab, mask_G_BOT)
    # cv2.imshow('23', mask_BOT)
    
    contours, _ = cv2.findContours(mask_BOT, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    demo = face.copy()
    cv2.drawContours(demo, [max(contours, key = cv2.contourArea)], 0, (0,255,0), 2)
    # cv2.imshow("24", demo)

    mask_BOT = np.zeros_like(mask_BOT)
    cv2.drawContours(mask_BOT, [max(contours, key = cv2.contourArea)], -1, 255, -1)
    # cv2.imshow("25", mask_BOT)

    mask_Mango = cv2.bitwise_or(mask_BOT, mask_TOP)
    # cv2.imshow('26', mask)
    kernel = np.ones((9,9),np.uint8)
    mask_Mango = cv2.erode(mask_Mango,kernel,iterations = 1)
    mask_Mango = cv2.dilate(mask_Mango,kernel,iterations = 1)
    # cv2.imshow('27', mask_Mango)
    # cv2.waitKey(0)

    contours, _ = cv2.findContours(mask_Mango, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mask_Mango = np.zeros_like(mask_Mango)
    cv2.drawContours(mask_Mango, [max(contours, key = cv2.contourArea)], -1, 255, -1)
    
    x,y,w,h = cv2.boundingRect(mask_Mango)
    mask_Mango = np.zeros_like(mask_Mango)
    cv2.ellipse(mask_Mango, (int(x+w/2), int(y+h/2)), (int(w/2)+2, int(h/2)+2), 0, 0, 360, 255, -1)   
    # cv2.imshow('27', mask_Mango)
    # cv2.waitKey(0)

    
    return mask_Mango


"""TÌM ĐIỂM CÓ TỌA ĐỘ Y NHỎ NHẤT, Y LỚN NHẤT, X NHỎ NHẤT, X LỚN NHẤT TRÊN ĐƯỜNG VIỀN QUẢ XOÀI
INPUT: contour: đường viền quả xoài
OUTPUT: điểm có tọa độ y nhỏ nhất, điểm có tọa độ x nhỏ nhất, điểm có tọa độ x lớn nhất, điểm có tọa độ y nhỏ nhất trên đường viền
"""
def find_TopBottomLeftRight(contour):
    sorted_points_X = sorted(contour, key=lambda c: c[:,0]) #sắp xếp các điểm có tọa độ x tăng dần
    sorted_points_Y = sorted(contour, key=lambda c: c[:,1]) #sắp xếp các điểm có tọa độ y tăng dần

    Top_points = sorted_points_Y[:2]#tìm hai điểm có tọa tọa độ y nhỏ nhất (hai điểm đầu tiên của mảng "sorted_points_Y")
    Top_point = (int(min(Top_points, key=lambda x : x[:,0])[0][0]+(abs(Top_points[0][0][0]-Top_points[1][0][0])/2)),
                 int(min(Top_points, key=lambda y : y[:,1])[0][1]+(abs(Top_points[0][0][1]-Top_points[1][0][1])/2))) #Tọa độ điểm ở giữa hai điểm vừa xác định

    Bottom_points = sorted_points_Y[-2:]#Tìm hai điểm có tọa y lớn nhất(hai điểm cuối cùng của mảng "sorted_points_Y")
    Bottom_point = (int(min(Bottom_points, key=lambda x : x[:,0])[0][0]+(abs(Bottom_points[0][0][0]-Bottom_points[1][0][0])/2)),
                    int(min(Bottom_points, key=lambda y : y[:,1])[0][1]+(abs(Bottom_points[0][0][1]-Bottom_points[1][0][1])/2))) #Tọa độ điểm ở giữa hai điểm vừa xác định

    Left_points = sorted_points_X[:2]#tìm hai điểm có tọa tọa độ x nhỏ nhất (hai điểm đầu tiên của mảng "sorted_points_X")
    Left_point = (int(min(Left_points, key=lambda x : x[:,0])[0][0]+(abs(Left_points[0][0][0]-Left_points[1][0][0])/2)),
                  int(min(Left_points, key=lambda y : y[:,1])[0][1]+(abs(Left_points[0][0][1]-Left_points[1][0][1])/2))) #Tọa độ điểm ở giữa hai điểm vừa xác định

    Right_points = sorted_points_X[-2:]#tìm hai điểm có tọa tọa độ x lớn nhất (hai điểm đầu tiên của mảng "sorted_points_X")
    Right_point = (int(min(Right_points, key=lambda x : x[:,0])[0][0]+(abs(Right_points[0][0][0]-Right_points[1][0][0])/2)),
                   int(min(Right_points, key=lambda y : y[:,1])[0][1]+(abs(Right_points[0][0][1]-Right_points[1][0][1])/2))) #Tọa độ điểm ở giữa hai điểm vừa xác định
    
    return Top_point, Left_point, Right_point, Bottom_point

"""TÌM GIAO ĐIỂM CỦA HAI ĐOẠN THẲNG ĐƯỢC TẠO THÀNH TỪ 4 ĐIỂM
INPUT: tọa độ hai điểm của của đoạn thẳng thứ nhất (A,B), tọa độ hai điểm của của đoạn thẳng thứ hai (C, D)
OUTPUT: tọa độ giao điểm của đoạn thảng AB và CD
"""
def find_intersection_point(A, B, C, D):
    # Tính hệ số A, B, C của đường thẳng AB
    A1 = B[1] - A[1]
    B1 = A[0] - B[0]
    C1 = A[0] * B[1] - A[1] * B[0]

    # Tính hệ số A, B, C của đường thẳng CD
    A2 = D[1] - C[1]
    B2 = C[0] - D[0]
    C2 = C[0] * D[1] - C[1] * D[0]

    # Tính giao điểm (x, y) bằng cách giải hệ phương trình tuyến tính
    determinant = A1 * B2 - A2 * B1
    if determinant == 0:
        # Hai đường thẳng là song song, không có giao điểm
        return None
    else:
        x = (B1 * C2 - B2 * C1) / determinant
        y = (A2 * C1 - A1 * C2) / determinant
        return abs(x), abs(y)
    
"""TÌM 4 ĐIỂM TRÊN ĐƯỜNG VIỀN CÓ TỌA ĐỘ GẦN ĐƯỜNG THẲNG NHẤT
INPUT: contour: đường viền chứa 4 điểm cần tìm, 
       a: đường thẳng cần đối chiểu (x = a hoặc y = a)
       axis = 1 đường thẳng đối chiếu nằm nggang (y = a)
       axis = 0 đường thẳng đối chiếu thẳng đứng (x = a)
OUTPUT: tọa độ 4 điểm trên đường viền gần đường thẳng nhất
"""
def points_nearest_line(contour, a, axis = 0):
    if axis == 0:
        left_points = []
        left_idx = []
        right_points = []
        right_idx = []
        idx = 0
        for point in contour:
            x = point[0][0]
            y = point[0][1]
            '''Tìm và lưu các điểm nằm về phía trái đường thẳng x = a'''
            if x < a:
                left_points.append((x, y))#Tọa độ điểm
                left_idx.append(idx)#Số thứ tự của điểm trong mảng contour
            '''Tìm và lưu các điểm nằm về phía phải đương thẳng x = a'''
            if x > a:
                right_points.append((x, y))
                right_idx.append(idx)
            idx+=1
        '''Tìm hai điểm hai điểm liền kề không liên tục nằm ở phía trái đường thẳng x = a'''
        break_left = None
        for i in range(len(left_idx)-1):
            if left_idx[i+1]-left_idx[i]!=1:
                break_left = i
                break
        if break_left is not None:#tìm thấy hai điểm liền kề không liên tục
            start_left = left_points[break_left+1]
            end_left = left_points[break_left]
        else:#không tìm thấy hai điểm liền kề không liên tục
            start_left = left_points[0]
            end_left = left_points[-1]
        
        '''Tìm hai điểm hai điểm liền kề không liên tục nằm ở phía phải đường thẳng x = a'''
        break_right = None
        for i in range(len(right_idx)-1):
            if right_idx[i+1]-right_idx[i]!=1:
                break_right = i
                break
        if break_right is not None:
            start_right = right_points[break_right]
            end_right = right_points[break_right+1]
        else:
            start_right = right_points[-1]
            end_right = right_points[0]
        return start_left, start_right, end_left, end_right

    if axis == 1:
        top_points = []
        top_idx = []
        bottom_points = []
        bottom_idx = []
        idx = 0
        for point in contour:
            x = point[0][0] #tọa độ x của một điểm
            y = point[0][1] #tọa độ y của một điểm
            '''Tìm và lưu các điểm nằm trên đường thảng y = a'''
            if y < a:
                top_points.append((x, y)) #Tọa độ điểm
                top_idx.append(idx) #Số thứ tự của điểm tỏng mảng "contour"
            '''Tìm và lưu các điểm nằm dưới đường thẳng y = a'''
            if y > a:
                bottom_points.append((x, y))
                bottom_idx.append(idx)
            idx+=1

        '''Tìm điểm liền kề không liên tục'''
        break_top = None
        for i in range(len(top_idx)-1):
            if top_idx[i+1]-top_idx[i]!=1:
                break_top = i
                break
        
        '''hai điểm gần nhất nằm trên đường thẳng y = a'''
        if break_top is not None:#Trường hợp có hai điểm liền kề không liên tục
            start_top = top_points[break_top]
            end_top = top_points[break_top+1]
            
        # else:#trường hợp không có hai điểm liên tục không liền kề
        #     start_top = top_points[-1]
        #     end_top = top_points[0]

        '''hai điểm gần nhất nằm dưới đường thẳng y = a'''
        start_bottom = bottom_points[0]
        end_bottom = bottom_points[-1]
        return start_top, start_bottom, end_top, end_bottom

"""CẮT LÁT MẶT XOÀI
INPUT: NumSlice: số lượng lát cắt,
       Width, Height: chiều ngang, chiều cao ảnh nhị phân
       Contour: đường viền của quả xoài đang cắt lát, 
       Ratio_Scale: danh sách tỷ lệ thu nhỏ của lát cắt theo hai trục,
       Offset_Slice: danh sách tọa độ dịch của lát cắt theo hai trục,
       center_y = True: trọng tâm lát cắt về giữa trục y khung hình (Dùng cho mặt xoài camera 1, camera 2)
OUTPUT: Mặt xoài đã cắt lát, danh sách lát cắt, cường độ xám của từng lát cắt, đường viền của từng lát cắt
"""
def slice_Face(NumSlice, Width, Height, Contour, Ratio_Scale, Offset_Slice, center_y = False):
    Slices = []
    ContourSlice = []
    SlicedFace = np.ones((Height, Width), np.uint8)
    Intensity = []
    First_slice = Contour
    for j in range(NumSlice):
        Contour_Scaled = First_slice * np.array(Ratio_Scale[j]) + np.array(Offset_Slice[j]) #tọa độ đường viền mới sau khi thu nhỏ và tịnh tiến theo hai trục x và y
        Contour_Scaled = Contour_Scaled.astype(int)#Chuyển về dạng mảng giống với ban đầu
        if center_y: #Căn giữa theo trục y
            M = cv2.moments(Contour_Scaled) #Tìm trọng tâm của quả xoài
            cy = int(M["m01"] / M["m00"])
            offset = Height/2-cy #Tìm khoảng dịch
            Contour_Scaled = Contour_Scaled + np.array((0, offset)) #Tọa độ đường viền mới
            Contour_Scaled = Contour_Scaled.astype(int)#Chuyển về dạng mảng giống với ban đầu

        ContourSlice.append(Contour_Scaled) #Lưu tập hợp điểm tạo thành lát cắt vào mảng
        slice = np.zeros((Height, Width), dtype=np.uint8)
        slice = cv2.drawContours(slice, [Contour_Scaled], 0, 255, -1) #vẽ lát cắt cắt lên mảng đen (màu trắng)
        # cv2.imshow("Slice", slice)
        # cv2.waitKey(0)
        Slices.append(slice) 

    '''Gắn mã màu cho lát cắt'''
    pxInt = 0  # Giá trị điểm ảnh (Gán lên mỗi lát cắt)
    noSlices = len(Slices)  # Số lát cắt
    for j in range(noSlices):
        currentSlice = Slices[j]
        pxInt += int(250 / noSlices)
        Intensity.append(pxInt)
        filter = np.ones((Height, Width), np.uint8) * pxInt
        if currentSlice is not Slices[-1]:
            nextSlice = Slices[j + 1]
            cutSlice = cv2.bitwise_xor(currentSlice, nextSlice)
            cutSlice = cv2.bitwise_and(cutSlice, filter)
        else:
            cutSlice = cv2.bitwise_and(Slices[j], filter)
        SlicedFace = cv2.bitwise_or(SlicedFace, cutSlice)
        j += 1
    return SlicedFace, Slices, Intensity, ContourSlice

"""XÁC ĐỊNH ẢNH NHỊ PHÂN VÀ ĐƯỜNG VIỀN KHUYẾT ĐIỂM.
INPUT: face: Ảnh gốc mặt xoài
       maskMango: Ảnh nhị phân mặt xoài
       cordinate_Box: Danh sách tọa độ điểm các ô vuông nhỏ trên ảnh
       plotsmall: True: thực hiện vẽ biểu đồ phân bố cường độ xám trong ô vuông/ False: không vẽ
       plotbig: True: thực hiện vẽ biểu đồ cường độ xám toàn bộ bề mặt xoài/ False: không vẽ
       tape: True: có dán giấy/ False: không dán giấy
OUTPUT: Ảnh nhị phân khuyết điểm và đường viền khuyết điểm 

    *** ĐỘ SÁNG TỐI CỦA ĐIỂM ẢNH: Độ tối-sáng ảnh xám có giá giá trị từ 0-255 <=> Tối(0)-Sáng(255)
    *** ĐẶC ĐIỂM KÊNH a HỆ MÀU Lab: Giảm được độ sáng tối của màu sắc
                                    Độ tương phản không cao
                                =>  Cần áp dụng tăng tương phản => dễ xuất hiện các điểm không phải khuyết điểm thật
                                    =>  Chỉ áp dụng được cho mảng lớn để tìm các khuyết điểm lớn
    *** ĐẶC ĐIỂM KÊNH G HỆ MÀU RGB: Bị ảnh hưởng bởi độ sáng tối của màu sắc
                                    Độ tương phản cao
                                    => Chỉ áp dụng cho một mảng nhỏ tương đối đều màu
"""
def find_DefectContours(face, maskMango, cordinate_Box, plotsmall = False, plotbig = False, tape = False):
    demo_contour = face.copy()
    """Tìm khuyết điểm có kích thước nhỏ"""
    gray = face[:,:,1]#kênh G hệ RGB
    # cv2.imshow("0",gray)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(maskMango, kernel, iterations=1)#bào mòn loại bỏ bớt phần rìa
    # cv2.imshow("1",mask)
    notmask = cv2.bitwise_not(mask)
    gray = cv2.bitwise_and(gray, mask)#Nhân ảnh xám với ảnh nhị mặt xoài
    # cv2.imshow("2",gray)
    # cv2.waitKey(0)

    defect = np.zeros_like(mask)
    if tape is False:
        for i in range (len(cordinate_Box)):
            blank = np.zeros_like(defect)
            cv2.rectangle(blank,cordinate_Box[i][0], cordinate_Box[i][1], 255, -1)#Vẽ vùng tìm khuyết điểm (ô chữ nhật màu trắng)
            # cv2.imshow("3",blank)
            # cv2.waitKey(0)
            smallgray = gray.copy()
            smallgray = cv2.bitwise_and(smallgray, blank)

            """Tìm ngưỡng"""
            if cv2.countNonZero(smallgray)!=0:
                histogram, bin_edges = np.histogram(smallgray, bins=255, range=(1, 256))#Biểu đồ phân bố cường độ xám

                '''Khử nhiễu dùng Trung bình động'''
                window_size = 11
                window = np.ones(window_size) / window_size
                filter_histogram = np.convolve(histogram, window, mode='same')

                '''Loại bỏ các điểm có mật độ pixel = 0 và tính trung bình mật độ pixel'''
                nonzero_values = filter_histogram[np.nonzero(filter_histogram)]
                average = np.mean(nonzero_values)
                index_TOP = None

                '''Tìm đỉnh đầu tiên của đồ thị'''
                for j in range(1, 254):
                    if filter_histogram[j]-filter_histogram[j-1]>=0 and filter_histogram[j]-filter_histogram[j+1]>=0 and filter_histogram[j]>=0.5*average:
                        index_TOP=j
                        break
                
                '''Tìm thời điểm đồ thị bắt đầu lõm'''
                thresh = 0
                if index_TOP is not None:
                    for k in list(reversed(range(index_TOP))):
                        if k>=1 and filter_histogram[k-1]-filter_histogram[k]>=0 and filter_histogram[k+1]-filter_histogram[k]>0:
                            thresh = k
                            break

                '''Tìm ảnh nhị phân khuyết điểm'''
                _, threshold_image = cv2.threshold(smallgray, thresh, 255, cv2.THRESH_BINARY)
                notBox = cv2.bitwise_not(blank)
                threshold_image = cv2.bitwise_or(threshold_image, notBox)
                threshold_image = cv2.bitwise_or(threshold_image, notmask)
                threshold_image = cv2.bitwise_not(threshold_image)
                defect = cv2.bitwise_or(defect, threshold_image)

                '''Vẽ biểu đồ phân bố cường độ xám trong ô chữ nhật'''
                if plotsmall:
                    fig, ax = plt.subplots(2, 3, figsize=(15, 9))

                    ax[0,0].set_title("Green Chanel")
                    ax[0,0].imshow(gray, cmap='gray')
                    ax[0,0].axis('off')

                    ax[1,0].set_title("Grayscale Histogram")
                    ax[1,0].plot(bin_edges[0:-1], histogram, label = "Histogram",color = 'pink')
                    ax[1,0].plot(bin_edges[0:-1], filter_histogram, label ="Moving average filter", color = 'blue')
                    ax[1,0].set_xlim(0, 256)
                    ax[1,0].set_xlabel("Grayscale value") 
                    ax[1,0].set_ylim(0, max(histogram) +2)
                    ax[1,0].set_ylabel("Pixels")  
                    ax[1,0].plot([thresh, thresh], [0, max(histogram) +2],'r--')
                    ax[1,0].plot([index_TOP, index_TOP], [0, max(histogram) +2],'b--')               
                    ax[1,0].plot([0,256], [average, average],'g--')
                    ax[1,0].legend()

                    ax[0,1].set_title("Box Green Chanel")
                    ax[0,1].imshow(smallgray, cmap='gray')
                    ax[0,1].axis('off')

                    ax[1,1].set_title("Binary Defect")
                    ax[1,1].imshow(threshold_image, cmap='gray')
                    ax[1,1].axis('off')

                    contours,hierarchy = cv2.findContours(threshold_image, 1, 2)
                    demo = face.copy()
                    demo = cv2.cvtColor(demo, cv2.COLOR_BGR2RGB)

                    ax[0,2].set_title("RGB Mango")
                    ax[0,2].imshow(demo)
                    ax[0,2].axis('off')

                    for cnt in contours:
                        cv2.drawContours(demo, [cnt], 0, (255,0,0), 1)
                    ax[1,2].set_title("Defect")
                    ax[1,2].imshow(demo)
                    ax[1,2].axis('off')

                    ax[1, 2].axis('off')

                    backend = matplotlib.get_backend()
                    if backend == 'TkAgg':
                        fig.canvas.manager.window.wm_geometry("+%d+%d" % (0, 0))
                    elif backend == 'WXAgg':
                        fig.canvas.manager.window.SetPosition((0, 0))
                    else:
                        # This works for QT and GTK
                        # You can also use window.setGeometry
                        fig.canvas.manager.window.move(0, 0)

                    plt.subplots_adjust(left= 0.079, bottom=0.05, right=0.983, top=0.88, wspace=0, hspace=0.29) 
                    plt.show()

        # cv2.imshow("4",defect)
        # cv2.waitKey(0)

        """Tìm khuyết điểm có kích thước lớn"""
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)[:,:,1]
        # cv2.imshow("0", gray)
        clahe = cv2.createCLAHE(clipLimit=6, tileGridSize=(11,11))#thông số tăng tương phản
        gray = clahe.apply(gray)#Áp đụng tăng tương phản
        # cv2.imshow("1", gray)
        gray = cv2.bitwise_and(gray, mask)
        # cv2.imshow('1.5', mask)
        # cv2.imshow("2", gray)
        # cv2.waitKey(0)

        histogram0, bin_edges = np.histogram(gray, bins=255, range=(1, 256))
        histogram = gaussian_filter(histogram0, 3)#Giảm răng cưa đồ thị bằng gaussian_filter
        index_MaxHIST = np.argmax(histogram)#Xác định số thứ tự của đỉnh đồ thị (giá trị cường độ xám)

        z_scores = (histogram - np.mean(histogram)) / np.std(histogram)#Tìm z_score
        indices = np.where(z_scores > 0)[0] #lọc ngưỡng loại outlier dựa vào z_score https://en.wikipedia.org/wiki/Standard_score
        upper_threshold = max(indices)

        blank = np.zeros_like(mask)
        blank[np.where((gray>[upper_threshold]))]=[255]#Lọc ngưỡng
        contours, _ = cv2.findContours(blank, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv2.contourArea(cnt)>100:#Tìm khuyết điểm có diện tích lớn hơn kích thước hình chữ nhật nhỏ phía trên
                cv2.drawContours(defect, [cnt], 0, 255, -1)

        '''Vẽ đồ thị phân bố cường độ xám trên toàn bộ bề mặt quả xoài'''
        if plotbig:
            fig, ax = plt.subplots(1,3, figsize = (20,4))
            ax[0].set_title("a Chanel")
            ax[0].imshow(gray, cmap='gray')
            ax[0].axis('off')

            ax[1].set_title("Grayscale Histogram")
            ax[1].plot(bin_edges[0:-1], histogram0, label = "Histogram", color = 'pink')
            ax[1].plot(bin_edges[0:-1], histogram, label = "Gaussian filter",color = 'blue')
            ax[1].set_xlim(0, 256)
            ax[1].set_xlabel("Grayscale value") 
            ax[1].set_ylim(0, max(histogram0) +2)
            ax[1].set_ylabel("Pixels")  
            ax[1].plot([index_MaxHIST, index_MaxHIST], [0, max(histogram0) +2],'b--')    
            # ax[1].plot([lower_threshold, lower_threshold], [0, max(histogram) +2],'y--')  
            ax[1].plot([upper_threshold, upper_threshold], [0, max(histogram0) +2],'r--')              
            ax[1].plot([0,256], [average, average],'g--')
            ax[1].legend(loc = 'upper right')

            bigdefect = np.zeros_like(blank)
            for cnt in contours:
                if cv2.contourArea(cnt)>50:
                    cv2.drawContours(bigdefect, [cnt], 0, 255, -1)
            ax[2].set_title("a Chanel")
            ax[2].imshow(bigdefect, cmap='gray')
            ax[2].axis('off')
            backend = matplotlib.get_backend()
            if backend == 'TkAgg':
                fig.canvas.manager.window.wm_geometry("+%d+%d" % (0, 0))
            elif backend == 'WXAgg':
                fig.canvas.manager.window.SetPosition((0, 0))
            else:
                # This works for QT and GTK
                # You can also use window.setGeometry
                fig.canvas.manager.window.move(0, 0)

            plt.subplots_adjust(left= 0.017, bottom=0.167, right=0.983, top=0.88, wspace=0.267, hspace=0.29) 
            plt.show()            


        cnt_Defect, _ = cv2.findContours(defect, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnt_Defect:
            cv2.drawContours(defect, [cnt], 0, 255, -1)

    else:
        _, defect = cv2.threshold(gray, 85, 255, cv2.THRESH_BINARY)

    
    cnt_Defect, _ = cv2.findContours(defect, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return cnt_Defect, defect

" cnt_Defect: tọa độ đường viền của tất cả các khuyết điểm"
" hình nhị phân của khuyết điểm"

"""TÌM PHẦN ĐƯỜNG VIỀN CHỨA ĐIỂM CÓ TỌA ĐỘ X, Y
INPUT: value: tọa độ x=value hoặc y=value của tâm khuyết điểm
        border: đường thẳng đi qua trọng tâm quả xoài (trục đứng x = border hoặc trùng nằm y = border)
        contour: đường viền quả xoài cần cắt
        mode: Top: Nếu tọa độ khuyết điểm nằm ở nửa trên đường viền, 
              Bottom: Nếu tọa độ khuyết điểm nằm ở nửa dưới đường viền
              Left: Nếu tọa độ khuyết điểm nằm ở nửa bên trái đường viền
              Right: Nếu tọa độ khuyết điểm nằm ở nửa bên phải đường viền 
OUTPUT: một một phần đường viền của đường viền quả xoài chứa điểm có tọa độ X, Y
"""
def cutContour(value, border, contour, mode):
    nearest_point = None
    idx_nearest_point = 0
    min_distance = float('inf')
    idx = 0
    if mode == 'Top':
        for point in contour:
            distance = abs(point[0][0] - value)
            #Tìm điểm thuộc đường viền có tọa độ x gần với tọa độ x của tâm khuyết điểm nhất và điểm này nằm phía trên đường thẳng y = border 
            if distance < min_distance and point[0][1] <= border:   
                nearest_point = point
                min_distance = distance
                idx_nearest_point = idx
            idx+=1
    elif mode == 'Left':
        for point in contour:
            distance = abs(point[0][1] - value)
            #Tìm điểm thuộc đường viền có tọa độ y gần với tọa độ y của tâm khuyết điểm nhất và điểm này nằm phía trái đường thẳng x = border
            if distance < min_distance and point[0][0] <= border:   
                nearest_point = point
                min_distance = distance
                idx_nearest_point = idx
            idx+=1
    elif mode == "Bottom":
        for point in contour:
            distance = abs(point[0][0] - value)
            #Tìm điểm thuộc đường viền có tọa độ x gần với tọa độ x của tâm khuyết điểm nhất và điểm này nằm phía dưới đường thẳng y = border 
            if distance < min_distance and point[0][1] >= border:   
                nearest_point = point
                min_distance = distance
                idx_nearest_point = idx
            idx+=1
    else: #Right
        for point in contour:
            distance = abs(point[0][1] - value)
            #Tìm điểm thuộc đường viền có tọa độ y gần với tọa độ y của tâm khuyết điểm nhất và điểm này nằm phía phải đường thẳng x = border
            if distance < min_distance and point[0][0] >= border:   
                nearest_point = point
                min_distance = distance
                idx_nearest_point = idx
            idx+=1

    '''Tìm tập hợp điểm tọa độ  thuộc đường viền có chứa tâm khuyết điểm'''
    numpoint = 7
    if idx_nearest_point<numpoint: #Trường hợp tâm khuyết điểm nằm ở đầu mảng "contour" (thuộc numpoint phần tử đầu tiên)
        contour_Crop = contour[0:idx_nearest_point+numpoint+1,:,:]
        contour_Crop = np.insert(contour_Crop, 0, contour[len(contour)-(numpoint-idx_nearest_point):len(contour)], 0)
    elif len(contour)-idx_nearest_point<numpoint: #Trường hợp tâm khuyết điểm nằm ở cuối mảng "contour" (thuộc numpoint phần tử cuối)
        contour_Crop = contour[idx_nearest_point-numpoint:len(contour)]
        contour_Crop = np.insert(contour_Crop, len(contour_Crop), contour[0:numpoint-(len(contour)-idx_nearest_point)], 0)
    elif idx_nearest_point == 0: #Trường hợp tâm khuyết điểm trùng với điểm đầu tiên của mảng "contour"  
        contour_Crop = contour[len(contour)-numpoint:0,:,:]  
        contour_Crop = np.insert (contour_Crop, 0, contour[0:numpoint], 0)
    else:
        contour_Crop = contour_Crop = contour[idx_nearest_point-numpoint:idx_nearest_point+numpoint+1,:,:] 

    # print(contour_Crop[7], nearest_point, len(contour_Crop))

    '''Do khoảng cách các giữa các điểm không đều nhau nên cần loại bỏ một số điểm thừa để đảm bảo tâm khuyết điểm nằm giữa phần đường viền vừa cắt'''
    D_nearest2firstPoint = np.linalg.norm(np.array(nearest_point[0]) - np.array(contour_Crop[0]))#Tính khoảng cách giữa tâm khuyết điểm và điểm đầu tiên của đường viền
    D_nearest2lastPoint = np.linalg.norm(np.array(nearest_point[0]) - np.array(contour_Crop[-1]))#Tính khoảng cách giữa tâm khuyết điểm và điểm cuối cùng của đường viền
    if D_nearest2firstPoint>D_nearest2lastPoint: #phần bên trái dài hơn so với phần bên phải
        #Lần lượt tính khoảng cách từ tâm khuyết điểm với các điểm nằm về phía bên trái mảng
        distance = [np.linalg.norm(np.array(nearest_point[0]) - np.array(point)) for point in contour_Crop[0:numpoint]]
        #Tìm số thứ tự của điểm có khoảng cách gần với giá trị "D_nearest2lastPoint" nhất
        index = np.abs(distance - D_nearest2lastPoint).argmin()
        #Phần đường viền sau khi cắt (đã loại bỏ một số điểm nằm về phía trái mảng)
        contour_Crop = contour_Crop[index: len(contour_Crop),:,:]
    elif D_nearest2firstPoint<D_nearest2lastPoint: #phần bên trái ngắn hơn so với phần bên phải
        #Lần lượt tính khoảng cách từ tâm khuyết điểm với các điểm nằm về phía bên phải mảng
        distance = [np.linalg.norm(np.array(nearest_point[0]) - np.array(point)) for point in contour_Crop[numpoint: len(contour_Crop)]]
        #Tìm số thứ tự của điểm có khoảng cách gần với giá trị "D_nearest2firstPoint" nhất
        index = np.abs(distance - D_nearest2firstPoint).argmin()
        #Phần đường viền sau khi cắt  (đã loại bỏ một số điểm nằm về phía bên phải mảng)
        contour_Crop = contour_Crop[0:numpoint+index+1,:,:]

    # print(D_nearest2lastPoint, D_nearest2firstPoint, distance[index])
    return contour_Crop, nearest_point[0]

"""TÌM ĐỘ NGHIÊNG CỦA PHẦN ĐƯỜNG VIỀN SAU KHI CẮT
INPUT: contourCrop: phần đường viền có chứa khuyết điểm
       axis: 0: góc nghiêng của phần đường viền so với trục Ox
             1: góc nghiêng của phần đường viền so với trục Oy
OUTPUT: góc nghiêng, vecto hướng của phần đường viền
"""
def findAngle(contourCrop, axis = 0):
    [vx, vy, x, y] = cv2.fitLine(contourCrop, cv2.DIST_L2, 0, 0.01, 0.01)#dùng thuật toán fitline để xác định hưỡng (trục chính của phần đường viền này)
    line = np.array([vx, vy])#Vecto chỉ phương
    if axis==0:
        axis = np.array([1, 0])#Vecto đơn vị của trục Ox
    else:
        axis = np.array([0, 1])#Vecto đơn vị của trục Oy
    '''Xác định góc nghiêng'''
    dot_product = np.dot(axis, line)
    angle = np.arccos(dot_product)
    return angle, [vx, vy, x, y]

"""GHÉP ẢNH
INPUT: imgList: danh sách các ảnh cần ghép
        mode = 0: ghép thành một hàng
        mode = 1: ghép thành 1 cột
OUTPUT: Ảnh
"""
def stackImages(imgList, mode):
    # Khởi tạo các biến
    width = []
    height = []
    image = []

    # Lưu kích thước của từng ảnh trong mảng.
    for img in imgList:
        width.append(img.shape[1])
        height.append(img.shape[0])

    # Lấy các kích thước lớn nhất.
    maxW = max(width)
    maxH = max(height)

    # Kiểm tra chế độ hoạt động.
    for element in imgList:
        if mode == 0:  # Ảnh được ghép thành hàng.
            expandingH = maxH - element.shape[0]
            borderImg = cv2.copyMakeBorder(element, expandingH, 0, 0, 0, cv2.BORDER_CONSTANT)
            image.append(borderImg)
        if mode == 1:  # Ảnh được ghép thành cột.
            expandingW = maxW - element.shape[1]
            borderImg = cv2.copyMakeBorder(element, 0, 0, expandingW, 0, cv2.BORDER_CONSTANT)
            image.append(borderImg)
    
    # Tiến hành ghép ảnh.
    if mode == 0:
        res = np.hstack(image)
    if mode == 1:
        res = np.vstack(image)

    return res

def plotArea(data, realArea, nameCam, show = False):
    error = []
    x_data = np.arange(0, len(data)) + 1
    for area in data:
        error.append(np.abs(realArea - area))
    print("Everage error: ", str(np.round(np.abs(np.mean(error)), 6)))
    print('Average area: ' + str(np.round(np.abs(np.mean(data)), 6)))
    
    fig, ax = plt.subplots()
    ax.text(1, 45, 'Average error: ' + str(np.round(np.abs(np.mean(error)), 2)) + " (%)",style='italic')
    ax.text(1, 43, 'Average area: ' + str(np.round(np.abs(np.mean(area)), 2)) + " ($mm^2$)",style='italic')

    ax.plot([0, len(data) + 1], [realArea, realArea], color="red")
    ax.bar(x_data, data, width=1, color = 'blue',edgecolor="white")
    # ax.scatter(x_data, data,color = 'blue')
    ax.set(xlim=(0, len(data) + 1), xticks=x_data, ylim=(0, 50))
    ax.set_title(f"Area defect {nameCam}", fontsize=15, style="oblique")
    ax.set_xlabel("Num of defect", fontsize=13)
    ax.set_ylabel("Area ($mm^2$)", fontsize=13)
    ax.set_xticklabels(x_data, rotation=90, fontsize=7)
    if show:
        plt.show()

def caculateError(data, realArea):
    error = []
    for area in data:
        error.append(np.abs(realArea - area))
    return np.round(np.abs(np.mean(error)), 6)
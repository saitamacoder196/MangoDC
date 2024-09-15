# Import các hằng số từ file config
from codev4.config import *
from codev4.myLib import Module as mod
from codev4.myLib.BaslerCamera import camera
from codev4.myLib.Control import control
from codev4.myLib.FindFace import find
from codev4.myLib.ImageProcess import Processing
from codev4.mysocket import WebSocketServer
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from time import sleep
from typing import Any, Dict
import asyncio
import cv2
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import tensorflow as tf
import threading
from codev4.services import save_mango_data, get_next_mango_id

# Load model (chỉ load một lần khi chương trình bắt đầu)
unet_model = tf.keras.models.load_model("models/rmbnet.keras")
mangoddsnet_model = tf.keras.models.load_model("models/mangoddsnet.keras")

def remove_background_from_image(image, model, img_size=(256, 256)):
    if image is None:
        print("Ảnh đầu vào không hợp lệ")
        return None

    original_size = image.shape[:2]  # Lưu kích thước gốc của ảnh

    # Resize ảnh về kích thước mà mô hình yêu cầu (256x256)
    resized_image = cv2.resize(image, img_size)
    
    # Chuẩn bị ảnh để dự đoán
    input_image = np.expand_dims(resized_image, axis=0) / 255.0  # Thêm batch size và normalize

    # Dự đoán mask bằng mô hình đã huấn luyện
    predicted_mask = model.predict(input_image)[0]
    
    # Resize mask về kích thước ban đầu của ảnh
    predicted_mask = cv2.resize(predicted_mask, original_size[::-1])
    
    # Chuyển mask về dạng nhị phân (0 và 1) và đảo ngược để giữ background
    binary_mask = (predicted_mask <= 0.5).astype(np.uint8)  # Giữ lại background thay vì foreground
    
    # Áp dụng mask ngược lên ảnh gốc để giữ lại phần background
    result = cv2.bitwise_and(image, image, mask=binary_mask)
    
    # Chuyển đổi các pixel màu đen thành màu trắng
    result[np.all(result == [0, 0, 0], axis=-1)] = [255, 255, 255]
    
    return result

def read_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Không thể đọc ảnh từ đường dẫn: {image_path}")
    return image

def create_mango_mask(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_mango = np.array([20, 20, 20])
    upper_mango = np.array([80, 255, 255])
    mango_mask = cv2.inRange(hsv, lower_mango, upper_mango)
    
    kernel = np.ones((5,5), np.uint8)
    mango_mask = cv2.morphologyEx(mango_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mango_mask = cv2.morphologyEx(mango_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    
    return mango_mask

def find_mango_contour(mango_mask):
    mango_contours, _ = cv2.findContours(mango_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not mango_contours:
        raise ValueError("Không tìm thấy đường viền xoài")
    return max(mango_contours, key=cv2.contourArea)


def create_disease_mask(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_brown = np.array([10, 100, 20])
    upper_brown = np.array([30, 255, 200])
    disease_mask = cv2.inRange(hsv, lower_brown, upper_brown)
    
    kernel = np.ones((5,5), np.uint8)
    disease_mask = cv2.morphologyEx(disease_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    disease_mask = cv2.morphologyEx(disease_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    return disease_mask

def find_disease_contours(disease_mask, min_area=10):
    disease_contours, _ = cv2.findContours(disease_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [cnt for cnt in disease_contours if cv2.contourArea(cnt) >= min_area]

def draw_contours(image, mango_contour, disease_contours):
    result = image.copy()
    cv2.drawContours(result, [mango_contour], -1, (0, 0, 255), 2)
    cv2.drawContours(result, disease_contours, -1, (0, 255, 0), 2)
    return result

def calculate_areas(mango_contour, disease_contours):
    mango_area = cv2.contourArea(mango_contour)
    total_disease_area = sum(cv2.contourArea(cnt) for cnt in disease_contours)
    disease_percentage = (total_disease_area / mango_area) * 100 if mango_area > 0 else 0
    return mango_area, total_disease_area, disease_percentage

def get_contour_center(contour):
    M = cv2.moments(contour)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    else:
        cX, cY = 0, 0
    return cX, cY

def cut_disease_bounding_boxes(image, disease_contours):
    bounding_boxes = []
    for contour in disease_contours:
        x, y, w, h = cv2.boundingRect(contour)
        bounding_box = image[y:y+h, x:x+w]
        bounding_boxes.append((bounding_box, (x, y, w, h)))
    return bounding_boxes

def preprocess_for_mangoddsnet(image, target_size=(224, 224)):
    resized_image = cv2.resize(image, target_size)
    normalized_image = resized_image / 255.0
    return np.expand_dims(normalized_image, axis=0)

def predict_disease(bounding_boxes, model):
    predictions = []
    for box, _ in bounding_boxes:
        preprocessed_box = preprocess_for_mangoddsnet(box)
        prediction = model.predict(preprocessed_box)
        if prediction.size > 0:
            predicted_class = np.argmax(prediction)
            predictions.append(predicted_class)
        else:
            predictions.append(None)  # Hoặc một giá trị mặc định khác
    return predictions

def process_single_image(image_path, unet_model, mangoddsnet_model):
    image = read_image(image_path)
    image_no_bg = remove_background_from_image(image, unet_model)
    if image_no_bg is None:
        raise ValueError("Lỗi khi remove background")
    
    mango_mask = create_mango_mask(image_no_bg)
    mango_contour = find_mango_contour(mango_mask)
    disease_mask = create_disease_mask(image_no_bg)
    disease_contours = find_disease_contours(disease_mask)
    
    if not disease_contours:
        print("Không phát hiện vùng bệnh")
        return image_no_bg, 0, cv2.contourArea(mango_contour), 0, [], [], []
    
    result_image = draw_contours(image_no_bg, mango_contour, disease_contours)
    mango_area, disease_area, disease_percentage = calculate_areas(mango_contour, disease_contours)
    
    bounding_boxes = cut_disease_bounding_boxes(image_no_bg, disease_contours)
    disease_predictions = predict_disease(bounding_boxes, mangoddsnet_model)
    
    return result_image, disease_area, mango_area, disease_percentage, disease_contours, bounding_boxes, disease_predictions

def analyze_single_mango_image(image_path, output_folder, unet_model, mangoddsnet_model):
    result_json = {
        "original_image": image_path,
        "processed_image": "",
        "mango_area": 0,
        "disease_area": 0,
        "disease_percentage": 0,
        "detected_diseases": [],
        "conclusion": ""
    }

    try:
        result_image, disease_area, mango_area, disease_percentage, disease_contours, bounding_boxes, disease_predictions = process_single_image(image_path, unet_model, mangoddsnet_model)
        
        base_name = os.path.basename(image_path)
        result_image_path = os.path.join(output_folder, f"processed_{base_name}")
        cv2.imwrite(result_image_path, result_image)
        
        result_json["processed_image"] = result_image_path
        result_json["mango_area"] = mango_area
        result_json["disease_area"] = disease_area
        result_json["disease_percentage"] = disease_percentage
        disease_names = ["DC", "DD", "DE","RD","TT"]  # Thay thế bằng tên thực tế của các loại bệnh
        
        for (_, (x, y, w, h)), prediction in zip(bounding_boxes, disease_predictions):
            if prediction is not None and prediction < len(disease_names):
                disease_name = disease_names[prediction]
            else:
                disease_name = "Unknown Disease"
            
            result_json["detected_diseases"].append({
                "position": {"x": x, "y": y},
                "size": {"width": w, "height": h},
                "area_size": w * h,
                "disease": disease_name
            })
        
        if disease_percentage > 10:
            result_json["conclusion"] = "Reject: Xoài bệnh"
        else:
            result_json["conclusion"] = "Accept: Không phát hiện dấu hiệu bệnh đáng kể"
        
    except Exception as e:
        result_json["error"] = str(e)
        print(f"Error processing {image_path}: {str(e)}")

    return result_json

def convert_and_analyze_mango_data(input_data: Dict[str, Any], 
                                   current_item: Dict[str, Any], 
                                   disease_thresholds: Dict[str, float]) -> Dict[str, Any]:
    result = {
        "current_item": current_item,
        "prediction_images": {},
        "original_images": {},
        "conclusion": {
            "detected_areas": [],
            "total_disease_area": 0,
            "total_mango_surface_area": 0,
            "disease_area_percentage": 0,
            "conclusion": ""
        }
    }

    total_disease_area = 0
    total_mango_surface_area = 0
    disease_counts = {}

    for image_key, image_data in input_data.items():
        # Cập nhật đường dẫn ảnh
        result["prediction_images"][image_key] = image_data["processed_image"]
        result["original_images"][image_key] = image_data["original_image"]

        # Cập nhật tổng diện tích
        total_mango_surface_area += image_data["mango_area"]
        total_disease_area += image_data["disease_area"]

        # Thêm thông tin về các vùng bệnh được phát hiện
        for disease in image_data["detected_diseases"]:
            result["conclusion"]["detected_areas"].append({
                "image": image_key,
                "position": disease["position"],
                "area_size": disease["area_size"],
                "disease": disease["disease"]
            })

            # Đếm số lượng từng loại bệnh
            if disease["disease"] not in disease_counts:
                disease_counts[disease["disease"]] = 0
            disease_counts[disease["disease"]] += disease["area_size"]

    # Cập nhật kết quả tổng hợp
    result["conclusion"]["total_disease_area"] = total_disease_area
    result["conclusion"]["total_mango_surface_area"] = total_mango_surface_area
    result["conclusion"]["disease_area_percentage"] = (total_disease_area / total_mango_surface_area * 100) if total_mango_surface_area > 0 else 0

    # Đưa ra kết luận
    conclusions = []
    for disease, area in disease_counts.items():
        if area > disease_thresholds.get(disease, 0):
            conclusions.append(f"Reject: Xoài bệnh {disease}")

    if not conclusions:
        conclusions.append("Accept: Không phát hiện dấu hiệu bệnh đáng kể.")

    result["conclusion"]["conclusion"] = "; ".join(conclusions)

    return result

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

        self.numMango = get_next_mango_id()

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
                    folder_name = os.path.join('static', 'mangoes', current_date, IMAGE_FOLDER)
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)

                    prediction_folder = os.path.join('static', 'mangoes', current_date, PREDICT_FOLDER)
                    if not os.path.exists(prediction_folder):
                        os.makedirs(prediction_folder)
                   
                    # Save images and collect the paths
                    pred_results = {}
                    for i in range(len(self.center)):
                        center_path = f"{folder_name}/{self.numMango}-Center_{i+1}.jpg"
                        cv2.imwrite(center_path, self.center[i])
                        pred_results[f"Center_{i+1}"] = analyze_single_mango_image(center_path, prediction_folder, unet_model, mangoddsnet_model) 

                    for i in range(len(self.left)):
                        left_path = f"{folder_name}/{self.numMango}-Left_{i+1}.jpg"
                        cv2.imwrite(left_path, self.left[i])
                        pred_results[f"Left_{i+1}"] = analyze_single_mango_image(left_path, prediction_folder, unet_model, mangoddsnet_model) 

                    # for i in range(len(self.right)):
                    #     right_path = f"{folder_name}/{self.numMango}-Right_{i+1}.jpg"
                    #     cv2.imwrite(right_path, self.right[i])
                    #     pred_results[f"Right_{i+1}"] = analyze_single_mango_image(right_path, prediction_folder, unet_model, mangoddsnet_model) 

                    current_item = {
                        "id": self.numMango,
                        "folder_path": current_date
                    }

                    disease_thresholds = {
                        "DC": 10,
                        "DD": 10,
                        "DE": 10,
                        "RD": 10,
                        "TT": 10
                    }

                    payload_results = convert_and_analyze_mango_data(pred_results, current_item, disease_thresholds)
                    saved_mango_item = save_mango_data(payload_results)

                    if saved_mango_item:
                        # Convert the dictionary to a JSON string
                        json_message = json.dumps(payload_results)
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
             
    def start(self):
        server_thread = threading.Thread(target=self.threadPool)
        server_thread.start()
        self.add_task(self.getFace)
        websocket_thread = threading.Thread(target=self.start_server)
        websocket_thread.start()
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
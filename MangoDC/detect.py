import cv2
import numpy as np
import io

def detect_and_analyze_mango_disease_bytes(image):
    # Ensure the image is in BGR format
    if len(image.shape) == 2:  # If grayscale, convert to BGR
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.shape[2] == 4:  # If RGBA, convert to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    
    original = image.copy()
    
    # Tạo mask cho quả xoài
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_mango = np.array([20, 20, 20])
    upper_mango = np.array([80, 255, 255])
    mango_mask = cv2.inRange(hsv, lower_mango, upper_mango)
    
    # Áp dụng morphological operations để làm sạch mask
    kernel = np.ones((5,5), np.uint8)
    mango_mask = cv2.morphologyEx(mango_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mango_mask = cv2.morphologyEx(mango_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # Tìm contour của quả xoài
    mango_contours, _ = cv2.findContours(mango_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not mango_contours:
        raise ValueError("Không tìm thấy quả xoài trong ảnh")
    mango_contour = max(mango_contours, key=cv2.contourArea)
    
    # Tính diện tích quả xoài
    mango_area = cv2.contourArea(mango_contour)
    
    # Định nghĩa phạm vi màu cho vết bệnh (nâu)
    lower_brown = np.array([10, 100, 20])
    upper_brown = np.array([30, 255, 200])
    
    # Tạo mask cho vết bệnh
    disease_mask = cv2.inRange(hsv, lower_brown, upper_brown)
    
    # Áp dụng morphological operations để làm sạch mask bệnh
    disease_mask = cv2.morphologyEx(disease_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    disease_mask = cv2.morphologyEx(disease_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Tìm contours của các vết bệnh
    disease_contours, _ = cv2.findContours(disease_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Lọc các contours
    min_area = 10  # Diện tích tối thiểu của vết bệnh
    filtered_disease_contours = [cnt for cnt in disease_contours if cv2.contourArea(cnt) >= min_area]
    
    # Tính tổng diện tích bệnh
    total_disease_area = sum(cv2.contourArea(cnt) for cnt in filtered_disease_contours)
    
    # Tính tỷ lệ phần trăm
    disease_percentage = (total_disease_area / mango_area) * 100 if mango_area > 0 else 0
    
    # Vẽ contours
    result = original.copy()
    cv2.drawContours(result, [mango_contour], -1, (0, 0, 255), 2)  # Vẽ contour xoài màu đỏ
    cv2.drawContours(result, filtered_disease_contours, -1, (0, 255, 0), 2)  # Vẽ contour bệnh màu xanh lá
    
    # Thêm thông tin vào ảnh
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(result, f"Disease: {disease_percentage:.2f}%", (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Chuyển đổi ảnh kết quả thành bytes
    _, buffer = cv2.imencode('.png', result)
    img_bytes = buffer.tobytes()
    
    return img_bytes, disease_percentage

# Hàm phụ trợ để đọc ảnh từ bytes
def read_image_from_bytes(img_bytes):
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

# Ví dụ sử dụng
if __name__ == "__main__":
    # Đọc ảnh từ file (thay thế bằng cách nhận bytes từ web trong ứng dụng thực tế)
    image_path = 'path_to_your_image.jpg'
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Không thể đọc ảnh từ {image_path}")
    else:
        try:
            result_bytes, disease_percentage = detect_and_analyze_mango_disease_bytes(image)
            print(f"Tỷ lệ diện tích bệnh: {disease_percentage:.2f}%")
            print(f"Kích thước của ảnh kết quả dạng bytes: {len(result_bytes)} bytes")
            
            # Để kiểm tra, bạn có thể lưu ảnh kết quả
            result_image = read_image_from_bytes(result_bytes)
            cv2.imwrite('result.png', result_image)
            print("Đã lưu ảnh kết quả vào 'result.png'")
        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")
import numpy as np
from PIL import Image, ImageOps
import cv2
from rembg import remove
import os
from scipy.spatial import distance

# Hàm remove background
def remove_background(image):
    fixed = remove(image)
    if fixed.mode == 'RGBA':
        fixed = fixed.convert('RGB')
    return fixed

# Hàm xử lý để tìm contour lớn nhất và trả về ROI
def find_largest_contour(image_cv):
    # Đảm bảo ảnh có 3 kênh (BGR) và là 8-bit
    if len(image_cv.shape) == 2:  # Nếu ảnh là grayscale
        image_cv = cv2.cvtColor(image_cv, cv2.COLOR_GRAY2BGR)
    elif image_cv.shape[2] == 4:  # Nếu ảnh có 4 kênh (có alpha)
        image_cv = cv2.cvtColor(image_cv, cv2.COLOR_BGRA2BGR)
    
    # Đảm bảo ảnh là 8-bit
    if image_cv.dtype != np.uint8:
        image_cv = cv2.convertScaleAbs(image_cv)
    
    blurred = cv2.GaussianBlur(image_cv, (5, 5), 0)
    newimg = np.zeros((image_cv.shape[0], image_cv.shape[1], 3), np.uint8)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    mean_shift_img = cv2.pyrMeanShiftFiltering(blurred, 20, 30, newimg, 0, criteria)
    blur_final = cv2.GaussianBlur(mean_shift_img, (11, 11), 1)
    edges = cv2.Canny(blur_final, 160, 290)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
    if contours:
        return max(contours, key=cv2.contourArea)
    else:
        return None

def process_image(image):
    image_cv = np.array(image)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)
    image_cv = cv2.resize(image_cv, (224, 224))
    original = image_cv.copy()

    p = 0
    for i in range(image_cv.shape[0]):
        for j in range(image_cv.shape[1]):
            B, G, R = image_cv[i, j]
            if B > 110 and G > 110 and R > 110:
                p += 1

    totalpixels = image_cv.shape[0] * image_cv.shape[1]
    per_white = 100 * p / totalpixels

    if per_white > 10:
        image_cv[np.where((image_cv[:, :, 0] > 110) & (image_cv[:, :, 1] > 110) & (image_cv[:, :, 2] > 110))] = [200, 200, 200]

    max_contour = find_largest_contour(image_cv)

    if max_contour is not None:
        cv2.drawContours(original, [max_contour], -1, (0, 0, 255), 3)
        original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        x, y, w, h = cv2.boundingRect(max_contour)
        roi = original_rgb[y:y+h, x:x+w]
        return Image.fromarray(original_rgb), Image.fromarray(roi)
    else:
        return image, None

# Hàm resize hình ảnh về kích thước 224x224
def resize_image(image):
    return image.resize((224, 224))

# Hàm chuyển đổi sang ảnh xám
def convert_to_grayscale(image):
    return ImageOps.grayscale(image)

# Hàm ngưỡng hóa ảnh xám
def threshold_image(image, threshold):
    image_np = np.array(image)
    _, thresh_image = cv2.threshold(image_np, threshold, 255, cv2.THRESH_BINARY)
    return Image.fromarray(thresh_image)

def group_contours(contours, threshold=50):
    groups = []
    used = set()

    for i, contour1 in enumerate(contours):
        if i in used:
            continue
        group = [contour1]
        used.add(i)
        for j in range(i + 1, len(contours)):
            if j in used:
                continue
            contour2 = contours[j]

            min_dist = np.inf
            for point1 in contour1:
                for point2 in contour2:
                    dist = distance.euclidean(point1[0], point2[0])
                    if dist < min_dist:
                        min_dist = dist

            if min_dist < threshold:
                group.append(contour2)
                used.add(j)
        groups.append(group)
    
    return groups

def find_convex_hulls_and_bounding_boxes(image, original_image, padding=10):
    image_np = np.array(image)

    if len(image_np.shape) == 3:
        image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(image_np, 50, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    groups = group_contours(contours, threshold=50)
    
    output_image = cv2.cvtColor(image_np, cv2.COLOR_GRAY2BGR)
    bounding_boxes = []

    for contour_group in groups:
        all_points = np.vstack(contour_group)
        min_x = np.min(all_points[:, 0, 0]) - padding
        max_x = np.max(all_points[:, 0, 0]) + padding
        min_y = np.min(all_points[:, 0, 1]) - padding
        max_y = np.max(all_points[:, 0, 1]) + padding

        hull = cv2.convexHull(all_points)
        cv2.polylines(output_image, [hull], True, (0, 255, 0), 2)

        cv2.rectangle(output_image, (min_x, min_y), (max_x, max_y), (0, 0, 255), 2)
        bounding_boxes.append((min_x, min_y, max_x, max_y))
    
    return Image.fromarray(output_image), bounding_boxes

def crop_and_save_bounding_boxes(original_image, bounding_boxes, folder_path, file_prefix):
    original_np = np.array(original_image)
    
    output_folder = os.path.join(folder_path, "DiseaseAreaDetect")
    os.makedirs(output_folder, exist_ok=True)

    cropped_images = []
    for idx, (min_x, min_y, max_x, max_y) in enumerate(bounding_boxes):
        # Chuyển đổi các giá trị thành kiểu int của Python
        min_x = int(min_x)
        min_y = int(min_y)
        max_x = int(max_x)
        max_y = int(max_y)

        # Kiểm tra kích thước bounding box để đảm bảo nằm trong phạm vi ảnh gốc
        if min_x < 0: min_x = 0
        if min_y < 0: min_y = 0
        if max_x > original_np.shape[1]: max_x = original_np.shape[1]
        if max_y > original_np.shape[0]: max_y = original_np.shape[0]

        # Cắt và lưu ảnh nếu không rỗng
        cropped_image = original_np[min_y:max_y, min_x:max_x]
        if cropped_image.size == 0:
            continue  # Bỏ qua nếu ảnh cắt ra là rỗng
        cropped_images.append(Image.fromarray(cropped_image))

        # Lưu ảnh đã cắt
        output_filename = f"{file_prefix}_box_{idx + 1}.png"
        output_filepath = os.path.join(output_folder, output_filename)
        cv2.imwrite(output_filepath, cropped_image)
    
    return cropped_images

def invert_black_and_white(image):
    image_np = np.array(image)
    
    black_threshold = 50
    white_threshold = 205

    black_pixels = np.all(image_np < black_threshold, axis=-1)
    white_pixels = np.all(image_np > white_threshold, axis=-1)
    
    image_np[black_pixels] = [255, 255, 255]
    image_np[white_pixels] = [0, 0, 0]
    
    return Image.fromarray(image_np)
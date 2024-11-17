import cv2
import numpy as np
import os
from myLib import Module as mod


class MSISDefectMeasurement:
    def __init__(self, scale_ratio=0.5, output_dir="debug_images"):
        """Các hằng số lấy từ ImageProcess.py"""
        # Kích thước box cho từng loại camera
        self.Box_Center = [21, 15]  # Dùng cho camera giữa
        self.Box_LeftRight = [13, 11]  # Dùng cho camera trái phải
        
        # Hệ số tính diện tích cho từng camera
        self.Func_ConstArea_Center = [abs(6.988941860465115e-06), abs(0.007519668639534884)]
        self.Func_ConstArea_Left = [abs(1.9089044265593567e-05), abs(-0.0028447316680080513)]
        self.Func_ConstArea_Right = [abs(-1.996435199999999e-05), abs(0.058740052719999984)]
        
        # Số lát cắt và offset
        self.NUM_SLICES = 10  # 10 lát như trong bài báo 
        self.EXCLUDED_SLICES = 4  # 4 lát ngoài loại bỏ
        self.Offset = 10  # Offset khi cắt xoài trong project gốc
        
        # Kích thước lát đầu/cuối được lấy từ project 
        self.EDGE_PIXEL_SIZE = {
            'outer': self.Func_ConstArea_Center[0],  # k1 cho ảnh cạnh  
            'inner': self.Func_ConstArea_Center[1]   # kn cho ảnh cạnh
        }
        self.SIDE_PIXEL_SIZE = {
            'outer': self.Func_ConstArea_Left[0],    # k1 cho ảnh mặt
            'inner': self.Func_ConstArea_Left[1]     # kn cho ảnh mặt  
        }

        self.scale_ratio = scale_ratio
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def calculate_slice_pixel_sizes(self, is_side_view):
        """
        Tính kích thước pixel cho từng lát cắt dựa trên vị trí và loại mặt
        Args:
            is_side_view: True nếu là ảnh mặt, False nếu là ảnh cạnh
        Returns:
            pixel_sizes: Danh sách kích thước pixel cho từng lát
        """
        if is_side_view:
            k1 = self.SIDE_PIXEL_SIZE['outer'] 
            kn = self.SIDE_PIXEL_SIZE['inner']
        else:
            k1 = self.EDGE_PIXEL_SIZE['outer']
            kn = self.EDGE_PIXEL_SIZE['inner']

        # Tính ki theo công thức từ bài báo
        pixel_sizes = []
        for i in range(self.NUM_SLICES):
            # Công thức nội suy tuyến tính từ k1 đến kn
            ki = k1 + (i/(self.NUM_SLICES-1)) * (kn - k1)
            pixel_sizes.append(ki)
        
        return pixel_sizes

    def save_debug_image(self, image, name):
        """Lưu ảnh debug với tên cụ thể"""
        filename = os.path.join(self.output_dir, f"{name}.jpg")
        cv2.imwrite(filename, image)

    def generate_slices(self, mango_mask):
        """Tạo và lưu các lát cắt"""
        slices = []
        current_mask = mango_mask.copy()
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        
        # Lưu mask ban đầu
        self.save_debug_image(mango_mask, "01_initial_mask")
        
        # Visualize tất cả lát cắt trong một ảnh
        all_slices_vis = np.zeros_like(mango_mask)
        
        for i in range(self.NUM_SLICES):
            num_iterations = 2 * (i + 1)
            eroded = cv2.erode(current_mask, kernel, iterations=num_iterations)
            slice_mask = cv2.subtract(current_mask, eroded)
            slices.append(slice_mask)
            
            # Tạo ảnh minh họa lát cắt với giá trị pixel khác nhau
            all_slices_vis = cv2.add(all_slices_vis, 
                                   (slice_mask > 0).astype(np.uint8) * ((i + 1) * 25))
            
            # Lưu từng lát cắt riêng lẻ
            self.save_debug_image(slice_mask, f"02_slice_{i+1}")
            current_mask = eroded

        # Lưu ảnh tổng hợp các lát cắt
        self.save_debug_image(all_slices_vis, "03_all_slices_visualization")
        
        return slices

    def calculate_area_for_slice(self, num_pixels, slice_index, is_side_view):
        k = self.Func_ConstArea_Center[0] * slice_index + self.Func_ConstArea_Center[1] if is_side_view else self.Func_ConstArea_Left[0] * slice_index + self.Func_ConstArea_Left[1]
        area = num_pixels * abs(k) * (1/self.scale_ratio**2)
        
        # Debug
        print(f"Slice {slice_index}:")
        print(f"  Pixels: {num_pixels}")
        print(f"  k: {k}")
        print(f"  Area: {area}")
        
        return area

    def get_box_coordinates(self, image, is_side_view=True):
        """
        Tạo lưới box với kích thước box phù hợp theo loại ảnh
        """
        h, w = image.shape[:2]
        
        # Chọn box size phù hợp
        if is_side_view:
            box_size = self.Box_Center  # [21,15] cho ảnh mặt
        else:
            box_size = self.Box_LeftRight  # [13,11] cho ảnh cạnh
            
        div_w = w/box_size[0]
        div_h = h/box_size[1]
        
        box_coordinates = []
        debug_grid = image.copy()
        
        for j in range(box_size[1]):
            for k in range(box_size[0]):
                point1 = (int(k*div_w), int(j*div_h))
                point2 = (int((k+1)*div_w), int((j+1)*div_h))
                box_coordinates.append([point1, point2])
                cv2.rectangle(debug_grid, point1, point2, (0, 255, 0), 1)
        
        self.save_debug_image(debug_grid, "grid_visualization")
        return box_coordinates

    def measure_defect_area(self, image, defect_contours, is_side_view=True):
        """Đo và lưu ảnh các bước xử lý"""
        # Lưu ảnh gốc
        self.save_debug_image(image, "00_original_image")

        # 1. Xác định vùng xoài
        mask_mango, mask_removed_stem = mod.get_CenterMask(image)
        self.save_debug_image(mask_mango, "04_mango_mask")
        self.save_debug_image(mask_removed_stem, "05_removed_stem_mask")

        # 2. Tạo các lát cắt
        slices = self.generate_slices(mask_removed_stem)

        # Vẽ contour khuyết điểm lên ảnh gốc để kiểm tra
        defect_visualization = image.copy()
        cv2.drawContours(defect_visualization, defect_contours, -1, (0,255,0), 2)
        self.save_debug_image(defect_visualization, "07_detected_defects")

        # 4. Tính diện tích và vẽ kết quả
        result_image = image.copy()
        total_area = 0
        
        # Tạo ảnh để visualize các vùng được chấp nhận/loại bỏ
        accepted_regions = np.zeros_like(mask_mango)
        rejected_regions = np.zeros_like(mask_mango)

        for idx, cnt in enumerate(defect_contours):
            defect = np.zeros_like(mask_mango)
            cv2.drawContours(defect, [cnt], -1, 255, -1)

            S1 = 0  # Diện tích trong vùng chấp nhận
            S2 = 0  # Diện tích trong vùng loại bỏ
            
            # Tạo ảnh minh họa cho từng khuyết điểm
            defect_slices_vis = np.zeros_like(mask_mango)
                
            for i in range(self.NUM_SLICES):
                slice_defect = cv2.bitwise_and(defect, slices[i])
                num_pixels = cv2.countNonZero(slice_defect)
                
                if num_pixels > 0:
                    # Tính diện tích cho lát cắt này
                    area = self.calculate_area_for_slice(num_pixels, i, is_side_view)
                    
                    if i >= self.EXCLUDED_SLICES:
                        S1 += area
                        defect_slices_vis = cv2.add(defect_slices_vis, 
                                                (slice_defect > 0).astype(np.uint8) * 255)
                    else:
                        S2 += area
                        defect_slices_vis = cv2.add(defect_slices_vis, 
                                                (slice_defect > 0).astype(np.uint8) * 128)

            # Lưu ảnh phân tích từng khuyết điểm
            self.save_debug_image(defect_slices_vis, f"08_defect_{idx+1}_slices")

            if S1 > 0.75 * S2:
                total_area += (S1 + S2)
                # Vẽ contour và diện tích
                cv2.drawContours(result_image, [cnt], -1, (0, 0, 255), 2)
                cv2.drawContours(accepted_regions, [cnt], -1, 255, -1)
                
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.putText(result_image, f'{S1 + S2:.1f}mm2',
                              (cx-20, cy), cv2.FONT_HERSHEY_SIMPLEX,
                              0.5, (255, 255, 255), 1)
            else:
                cv2.drawContours(rejected_regions, [cnt], -1, 255, -1)

        # Lưu các ảnh kết quả cuối cùng
        self.save_debug_image(accepted_regions, "09_accepted_defects")
        self.save_debug_image(rejected_regions, "10_rejected_defects")
        self.save_debug_image(result_image, "11_final_result")

        return total_area, result_image
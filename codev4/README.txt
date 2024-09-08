"ArduinoController": thư mục chứa chương trình đã nạp xuống Arduino
"Calib": thư mục dùng để calib hệ thống.
"Check Accuracy": thư mục dùng để đánh giá độ chính xác của giải thuật tính diện tích khuyết điểm
"Image Mango": thư mục chứa ảnh bề mặt quả xoài
"myLib": Thư mục chứa các thư viện hỗ trợ cho việc xử lý ảnh và truyền thông với Arduino
'main.py': Chương trình tổng khi chạy cùng hệ thống, chương trình này thực chất là chương trình gọi các chương trình con trong thư mục trong myLib
'Processing.py': Chương trình xử lý ảnh, chạy riêng lẻ khi không có phần cứng, chương trình này đọc ảnh từ thư mục Image Mango để tính diện tích khuyết điểm của mỗi trái.
'RenameImage.py': Chương trình đổi tên thứ tự ảnh trong thư mục ảnh (Do trong quá trình chụp ảnh, có thể xảy ra một số sai sót dẫn đến đặt sai số thứ tự quả xoài), 
và lọc ra 4 mặt chính của quả xoài (Do bộ ảnh mới được chụp cách nhau 30 độ nên cần lọc lại cho đúng với số lượng ảnh khi báo cáo luận văn)
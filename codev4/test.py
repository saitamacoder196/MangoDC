import threading
import time
import websocket
import json

class RunTest:
    def __init__(self, ws_url):
        self.running = False
        self.thread = None
        self.ws_url = ws_url
        self.ws = None

    # Phương thức kết nối tới WebSocket server
    def connect_socket(self):
        try:
            self.ws = websocket.WebSocketApp(self.ws_url,
                                             on_message=self.on_message,
                                             on_error=self.on_error,
                                             on_close=self.on_close,
                                             on_open=self.on_open)
            # Chạy WebSocket trong một thread riêng
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.start()
            print(f"Connected to WebSocket at {self.ws_url}")
        except Exception as e:
            print(f"WebSocket error: {e}")
            self.stop()

    def on_open(self, ws):
        print("WebSocket connection opened")
        # Bắt đầu vòng lặp sau khi WebSocket kết nối thành công
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.start()

    # Phương thức xử lý nhận tin nhắn từ WebSocket server
    def on_message(self, ws, message):
        print(f"Received message: {message}")

    # Phương thức xử lý lỗi từ WebSocket
    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    # Phương thức xử lý đóng kết nối WebSocket
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    # Phương thức start sẽ bắt đầu vòng lặp để thực hiện processing
    def start(self):
        if not self.running:  # Chỉ bắt đầu nếu chưa chạy
            self.running = True
            self.connect_socket()  # Kết nối WebSocket và sau đó bắt đầu vòng lặp

    # Phương thức này dừng vòng lặp lại và đóng WebSocket
    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()  # Đóng WebSocket khi dừng
            print("WebSocket closed")

    # Phương thức chạy vòng lặp và gọi processing
    def _run_loop(self):
        while self.running:
            self.processing()
            time.sleep(1)  # Đợi 1 giây trước khi tiếp tục

    # Phương thức processing sẽ gửi text qua WebSocket mỗi 1 giây
    def processing(self):
        # Kiểm tra xem WebSocket có kết nối không
        if self.ws and self.ws.sock and self.ws.sock.connected:
            message = {"message": "Test message from client"}
            try:
                print(f"Sending: {message}")
                self.ws.send(json.dumps(message))  # Gửi message dưới dạng JSON
            except Exception as e:
                print(f"Error sending message: {e}")
                self.stop()
        else:
            print("WebSocket is not connected or has been closed")
            self.stop()


# Cách sử dụng class
if __name__ == "__main__":
    ws_url = 'ws://localhost:8000/ws/socket-server/'  # Địa chỉ WebSocket

    test = RunTest(ws_url)

    try:
        # Chạy vòng lặp
        test.start()

        # Dừng sau 5 giây
        time.sleep(5)
        test.stop()
        print("Stopped!")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        test.stop()

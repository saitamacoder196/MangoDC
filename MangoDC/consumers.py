# consumers.py
from channels.generic.websocket import WebsocketConsumer
import json

class MyConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()  # Kết nối được chấp nhận khi client kết nối thành công

    def disconnect(self, close_code):
        pass  # Xử lý khi client ngắt kết nối

    def receive(self, text_data):
        # Nhận tin nhắn từ client và gửi phản hồi
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')

        # Gửi tin nhắn về lại cho client
        self.send(text_data=json.dumps({
            'message': f"Server received: {message}"
        }))

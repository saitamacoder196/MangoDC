import asyncio
import websockets
import json
from threading import Thread

class WebSocketServer:
    clients = set()  # Tập hợp để giữ các client kết nối
    server_task = None

    def __init__(self):
        self.running = False

    async def register(self, websocket):
        # Đăng ký client mới
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")

    async def unregister(self, websocket):
        # Gỡ bỏ client khi ngắt kết nối
        self.clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.clients)}")

    async def send_message(self, message):
        # Gửi tin nhắn đến tất cả các client đang kết nối
        if self.clients:
            print(f"Sending message: {message}")
            await asyncio.wait([client.send(message) for client in self.clients])

    async def handle_client(self, websocket, path):
        # Xử lý kết nối từ client
        await self.register(websocket)
        try:
            async for message in websocket:
                print(f"Received message from client: {message}")
                # Nếu cần, xử lý tin nhắn từ client (ví dụ: echo lại hoặc phản hồi)
        finally:
            await self.unregister(websocket)

    async def periodic_send(self):
        # Chu kỳ gửi tin nhắn xuống các client
        while self.running:
            message = json.dumps({"message": "Periodic message from server"})
            await self.send_message(message)
            await asyncio.sleep(5)  # Gửi mỗi 5 giây

    def start_server(self):
        # Tạo event loop riêng cho thread này
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.running = True

        # Đặt WebSocket server trên cổng khác, ví dụ 8001
        start_server = websockets.serve(self.handle_client, "localhost", 8001)

        # Chạy server và chu kỳ gửi tin nhắn song song
        self.loop.run_until_complete(start_server)
        self.server_task = self.loop.create_task(self.periodic_send())
        self.loop.run_forever()

    def start(self):
        # Bắt đầu server trong một thread riêng
        server_thread = Thread(target=self.start_server)
        server_thread.start()

    def stop(self):
        # Hàm dừng server WebSocket
        self.running = False
        if self.server_task:
            self.server_task.cancel()
        self.loop.stop()
        print("WebSocket server stopped")
import asyncio
import inspect
import websockets
import json
from threading import Thread

class WebSocketServer:
    clients = set()  # Set to keep track of connected clients
    server_task = None

    def __init__(self):
        self.running = False
        self.tasks = []  # List to store tasks (functions with arguments)

    async def register(self, websocket):
        # Register a new client
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")

    async def unregister(self, websocket):
        # Unregister a client upon disconnection
        self.clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.clients)}")

    async def send_message(self, message):
        # Send message to all connected clients
        if self.clients:
            print(f"Sending message: {message}")
            disconnected_clients = set()
            tasks = []
            
            for client in self.clients:
                try:
                    # Create a task to send message
                    tasks.append(client.send(message))
                except Exception as e:
                    print(f"Error sending message to client: {e}")
                    disconnected_clients.add(client)
            
            if tasks:
                # Use asyncio.gather to await all tasks and catch any exceptions
                try:
                    await asyncio.gather(*tasks)
                except Exception as e:
                    print(f"Error during message send: {e}")

            # Remove clients that were disconnected
            for client in disconnected_clients:
                await self.unregister(client)


    async def handle_client(self, websocket, path):
        # Handle client connection
        await self.register(websocket)
        try:
            async for message in websocket:
                print(f"Received message from client: {message}")
                # Process the message from the client if needed
        finally:
            await self.unregister(websocket)

    def add_task(self, func, *args):
        # Add a task (function with its arguments) to the task list
        self.tasks.append((func, args))
        print(f"Added task: {func.__name__} with args: {args}")

    async def run_tasks(self):
        # Sequentially run tasks from the task list
        while self.running:
            if self.tasks:
                print("Running tasks...")
                for task, args in self.tasks:
                    if inspect.iscoroutinefunction(task):
                        # If the task is a coroutine, await it
                        await task(*args)
                    else:
                        # Otherwise, just call the task
                        task(*args)
                self.tasks.clear()  # Clear tasks after execution
            await asyncio.sleep(1)  # Sleep for a short while before checking again

    def start_server(self):
        # Create a new event loop for this thread
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.running = True

        # Set up the WebSocket server on a different port, e.g., 8001
        start_server = websockets.serve(self.handle_client, "localhost", 8001)

        # Run the server and the run_tasks task in parallel
        self.loop.run_until_complete(start_server)
        self.server_task = self.loop.create_task(self.run_tasks())
        self.loop.run_forever()

    def start(self):
        # Start the WebSocket server in a separate thread
        server_thread = Thread(target=self.start_server)
        server_thread.start()

    def stop(self):
        # Stop the WebSocket server
        self.running = False
        if self.server_task:
            self.server_task.cancel()
        self.loop.stop()
        print("WebSocket server stopped")

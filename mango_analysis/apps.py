import threading
import socket
from django.apps import AppConfig


class MangoAnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mango_analysis'

    # Class-level variable to store the server thread status
    server_thread = None
    server_running = False

    def ready(self):
        from codev4.main import RunTime

        # Function to check if the port is in use
        def is_port_in_use(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('127.0.0.1', port))
                except socket.error:
                    return True
                return False

        # Check if the port 8001 is in use
        if is_port_in_use(8001):
            print("Port 8001 is already in use. Server won't be started.")
            return

        # Check if the server is already running
        if not MangoAnalysisConfig.server_running:
            print("Starting server in a new thread...")
            server = RunTime()

            # Start the server in a new thread
            MangoAnalysisConfig.server_thread = threading.Thread(target=server.start)
            MangoAnalysisConfig.server_thread.start()
            MangoAnalysisConfig.server_running = True
        else:
            print("Server is already running.")
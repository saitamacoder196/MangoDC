# mango_analysis/apps.py
import threading
from django.apps import AppConfig



class MangoAnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mango_analysis'

    def ready(self):
        from codev4.main import RunTime
        server = RunTime()

        # Check if the server is running and start it in a separate thread if not
        if server and not server.running:  # Check if the server exists and isn't running
            print("Starting server in a new thread...")
            threading.Thread(target=server.start).start()  # Start the server in a new thread
        else:
            print("Server is already running or not defined.")

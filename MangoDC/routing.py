# routing.py
from django.urls import path
from .consumers import MyConsumer

websocket_urlpatterns = [
    path('ws/socket-server/', MyConsumer.as_asgi()),
]

from django.urls import re_path
from user import consumers

websocket_urlpatterns = [
    re_path(r'ws/some_path/$', consumers.ChatConsumer.as_asgi()),  # Correct WebSocket URL path
]

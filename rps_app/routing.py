# routing.py
from django.urls import re_path
from rps_app import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+_\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
# rps_project/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Set the default Django settings module early
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rps_project.settings')

# Initialize Django ASGI app (this loads basic settings)
django_asgi_app = get_asgi_application()

# Now safe to call setup for full Django initialization (models, etc.)
import django
django.setup()

# Now import your app-specific routing (these can safely access models/settings)
import attendance.routing  # For attendance app websockets (if applicable)
import rps_app.routing    # For rps_app (chat) websockets

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            attendance.routing.websocket_urlpatterns +  # Include attendance patterns
            rps_app.routing.websocket_urlpatterns       # Include rps_app patterns
        )
    ),
})
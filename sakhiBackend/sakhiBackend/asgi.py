import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from user import routing  # Import the routing file from the user app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sakhiBackend.settings')

application = ProtocolTypeRouter({
    # HTTP routing (default Django HTTP handling)
    "http": get_asgi_application(),
    
    # WebSocket routing
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns  # Make sure you are pointing to the correct routing file
        )
    ),
})

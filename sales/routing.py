# sales/routing.py
from django.urls import re_path
from sales.consumers import OmniCommandConsumer # <--- Importamos el consumidor blindado

websocket_urlpatterns = [
    # Mapeamos la ruta al endpoint de comando táctico
    re_path(r'ws/omni-hydra/$', OmniCommandConsumer.as_asgi()),
]
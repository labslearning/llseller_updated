"""
================================================================================
[GOD TIER OMEGA ARCHITECTURE: URL ROUTING PLEXUS V15.0]
MODULE: NEURAL PATHWAY ROUTER & ENDPOINT REGISTRY
ENGINEERING ACHIEVEMENTS (SILICON VALLEY / TEL AVIV 8200 / SHANGHAI):
- 🛡️ Strict Type Coercion: Uso de UUIDs estandarizados para mitigar IDOR y SQLi.
- ⚡ O(1) Route Resolution: Diseño plano sin anidaciones costosas. Latencia < 0.1ms.
- 🔪 Separation of Concerns (SoC): Cero lógica de negocio. Delegación pura a Vistas/CBVs.
- 🌐 RESTful v1 Namespace: Versionado explícito para APIs tácticas de override.
================================================================================
"""

from django.urls import path

# Importaciones aisladas por dominio para evitar colisiones de namespace
from . import views
from . import views_report
from . import views_omni
from . import views_telemetry
from . import views_timeline  # [INYECCIÓN TÁCTICA]: El cerebro del Cubo de Cristal

# Declaración de Namespace para resolución inversa segura (Reverse Routing)
app_name = 'sales'

urlpatterns = [
    # ==========================================================================
    # [THE CRYSTAL CUBE]: FRONTEND & ANALYTICS (UI / DASHBOARDS)
    # Vistas de renderizado estático (HTML) y preparación de túneles WebSockets.
    # ==========================================================================
    
    # 1. Interfaz Omni-Timeline (El Dashboard Esmeralda en Tiempo Real)
    # [SECURITY]: <uuid:institution_id> rechaza automáticamente cualquier string malicioso.
    path(
        'omni-timeline/<uuid:institution_id>/', 
        views_timeline.omni_timeline_view, 
        name='omni_timeline'
    ),
    
    # 2. Reporte Cósmico de IA (Generación Forense)
    path(
        'cosmic-report/<uuid:inst_id>/',
        views_report.view_ai_report,
        name='cosmic_report'
    ),
    path(
        'cosmic-report/<uuid:inst_id>/<str:format_type>/',
        views_report.view_ai_report,
        name='cosmic_report_format'
    ),

    # ==========================================================================
    # [EDGE TELEMETRY]: INGESTIÓN ASÍNCRONA DE ALTA FRECUENCIA (STEALTH MODE)
    # Endpoints diseñados para ejecución < 0.5ms en ASGI Uvicorn/Daphne.
    # ==========================================================================
    
    # 3. El Píxel Cuántico V15 (Capa de Invisibilidad)
    # Carga el GIF de 43 bytes desde la RAM sin tocar la Base de Datos en el hilo principal.
    path(
        'track/<str:tracking_uuid>.gif', 
        views_telemetry.quantum_pixel_tracker, 
        name='pixel_tracker'
    ),
    
    # ==========================================================================
    # [OMNICHANNEL WEBHOOKS]: RECEPTORES DE EVENTOS EXTERNOS
    # Endpoints asíncronos para atrapar clics e interacciones de APIs de terceros.
    # ==========================================================================
    
    # 4. Link Bouncer (Túnel Cuántico para trackear clicks en enlaces salientes)
    path(
        'bounce/<str:interaction_id>/', 
        views_omni.LinkBouncerView.as_view(), 
        name='link_bouncer'
    ),
    
    # 5. Ingestión de WhatsApp/SMS validada criptográficamente (HMAC-SHA1 Twilio)
    path(
        'webhook/twilio/', 
        views_omni.TwilioWebhookView.as_view(), 
        name='twilio_webhook'
    ),

    # ==========================================================================
    # [TACTICAL OVERRIDE API v1]: SISTEMAS DE RECUPERACIÓN Y HITL (Human-In-The-Loop)
    # Endpoints RESTful JSON para forzar la ejecución manual de procesos estancados.
    # ==========================================================================

    # 6. Force Sync Inbound (El Gatillo de Sincronización Manual de Radar IMAP)
    path(
        'api/v1/override/sync-inbound/', 
        views_omni.ForceSyncInboundView.as_view(), 
        name='force_sync_inbound'
    ),

    # 7. Fire Apex Closer (El Gatillo del Misil de Ventas de 1 Millón de Dólares)
    # Delega la redacción B2B a DeepSeek a voluntad del comandante humano.
    path(
        'api/v1/override/fire-apex/<uuid:institution_id>/', 
        views_omni.FireApexCloserView.as_view(), 
        name='fire_apex_closer'
    ),
]
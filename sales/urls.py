"""
================================================================================
[GOD TIER OMEGA ARCHITECTURE: URL ROUTING PLEXUS V10.1]
================================================================================
"""

from django.urls import path
from . import views
from . import views_report
from . import views_omni
from . import views_telemetry

app_name = 'sales'

urlpatterns = [
    # ==========================================================================
    # [THE CRYSTAL CUBE]: FRONTEND & ANALYTICS (UI / DASHBOARDS)
    # Vistas de renderizado estático y preparación de WebSockets.
    # ==========================================================================
    
    # 1. Interfaz Omni-Timeline (El Dashboard de WebSockets en Tiempo Real)
    # [FIX]: Apuntamos a views.py en lugar de views_omni.py
    path(
        'omni-timeline/<str:entity_id>/', 
        views.omni_timeline_view, 
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
    
    # 3. El Píxel Cuántico V10 (Capa de Invisibilidad)
    path(
        'track/<str:tracking_uuid>.gif', 
        views_telemetry.quantum_pixel_tracker, 
        name='pixel_tracker'
    ),
    
    # ==========================================================================
    # [OMNICHANNEL WEBHOOKS]: RECEPTORES DE EVENTOS EXTERNOS
    # Endpoints asíncronos para atrapar clics e interacciones de WhatsApp/SMS.
    # ==========================================================================
    
    # 4. Link Bouncer (Túnel Cuántico para trackear clicks en enlaces)
    path(
        'bounce/<str:interaction_id>/', 
        views_omni.LinkBouncerView.as_view(), 
        name='link_bouncer'
    ),
    
    # 5. Ingestión de WhatsApp/SMS validada criptográficamente
    path(
        'webhook/twilio/', 
        views_omni.TwilioWebhookView.as_view(), 
        name='twilio_webhook'
    ),
]
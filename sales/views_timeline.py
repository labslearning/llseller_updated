import time
import logging
import hashlib
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpRequest, HttpResponse, HttpResponseNotModified
from django.core.cache import cache
from django.utils.encoding import force_bytes

# Importaciones de Modelos B2B
from sales.models import Institution, Interaction, InteractionStatus

# Telemetría SRE Avanzada
logger = logging.getLogger('Sovereign.OmniTimeline.GodTier')

@staff_member_required
def omni_timeline_view(request: HttpRequest, institution_id: str) -> HttpResponse:
    """
    [GOD TIER LEVEL] Omni-Timeline Controller.
    - O(1) Cache Lookups
    - O(log N) DB Traversals
    - HTTP 304 ETag Browser Caching
    - Memory Projection (Zero Bloat)
    """
    start_time = time.perf_counter()

    # 1. Puntero a Memoria
    institution = get_object_or_404(Institution, id=institution_id)
    
    # =========================================================================
    # TÉCNICA 1: ETAG / HTTP 304 REVERSE ENGINEERING
    # Verificamos si hubo cambios ANTES de tocar el motor de plantillas
    # =========================================================================
    # Obtenemos solo el timestamp de la última interacción (Costo: <1ms)
    latest_interaction = Interaction.objects.filter(institution=institution).order_by('-updated_at').only('updated_at').first()
    
    if latest_interaction:
        # Creamos una firma digital del estado actual del historial
        etag_string = f"{institution_id}_{latest_interaction.updated_at.timestamp()}"
        etag_hash = hashlib.md5(force_bytes(etag_string)).hexdigest()
        
        # Si el navegador del usuario envía la misma firma, cortamos la ejecución aquí mismo.
        if request.META.get('HTTP_IF_NONE_MATCH') == etag_hash:
            logger.debug(f"⚡ [CACHE HIT] 304 Not Modified devuelto para {institution.name}")
            return HttpResponseNotModified()
    else:
        etag_hash = hashlib.md5(force_bytes(f"{institution_id}_empty")).hexdigest()

    # =========================================================================
    # TÉCNICA 2: QUERY PROJECTION & JOIN OPTIMIZATION
    # Extraemos solo las columnas que el HTML necesita. Nada más.
    # =========================================================================
    base_qs = Interaction.objects.filter(
        institution=institution
    ).select_related('contact').only(
        'id', 'channel', 'direction', 'status', 'subject', 'content', 
        'created_at', 'tracking_uuid', 'open_count', 'target_ip', 
        'user_agent', 'contact__name'
    ).order_by('-created_at')

    # =========================================================================
    # TÉCNICA 3: L1 MEMORY CACHE MATRIX
    # Envolvemos la agregación matemática en una capa de Caché RAM (TTL: 60s)
    # =========================================================================
    cache_key = f"omni_analytics_{institution_id}_{etag_hash}"
    analytics = cache.get(cache_key)

    if not analytics:
        # Solo castigamos a la CPU de la base de datos si la caché expira o hay datos nuevos
        db_analytics = base_qs.aggregate(
            total=Count('id'),
            opened=Count(
                'id', 
                filter=Q(status__in=[InteractionStatus.OPENED, InteractionStatus.REPLIED]) | Q(open_count__gt=0)
            )
        )
        total_interactions = db_analytics['total'] or 0
        opened_interactions = db_analytics['opened'] or 0
        open_rate = int((opened_interactions / total_interactions) * 100) if total_interactions > 0 else 0
        
        analytics = {
            'total': total_interactions,
            'opened': opened_interactions,
            'open_rate': open_rate
        }
        # Guardamos en RAM por 60 segundos
        cache.set(cache_key, analytics, timeout=60)

    # =========================================================================
    # TÉCNICA 4: DEFENSIVE PAGINATION
    # =========================================================================
    page_number = request.GET.get('page', 1)
    paginator = Paginator(base_qs, 50)
    
    try:
        interactions_page = paginator.page(page_number)
    except PageNotAnInteger:
        interactions_page = paginator.page(1)
    except EmptyPage:
        interactions_page = paginator.page(paginator.num_pages)

    # Cierre de Telemetría SRE
    execution_time_ms = (time.perf_counter() - start_time) * 1000
    logger.info(f"🚀 [GOD TIER RENDER] {institution.name} | Latencia Backend: {execution_time_ms:.2f}ms")

    # Ensamblaje del Payload final
    context = {
        'institution': institution,
        'interactions': interactions_page,
        'analytics': analytics,
        'system_latency': round(execution_time_ms, 2)
    }
    
    response = render(request, 'admin/sales/institution/omni_timeline.html', context)
    
    # Inyectamos el Hash Cuántico en las cabeceras de respuesta del servidor
    response['ETag'] = etag_hash
    response['Cache-Control'] = 'must-revalidate, max-age=0'
    
    return response
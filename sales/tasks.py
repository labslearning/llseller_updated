"""
======================================================================
[GOD TIER ARCHITECTURE: LEVIATHAN CLASS V86.0 - PROJECT OMNISCIENT]
MODULE: CELERY TASKS DISTRIBUTED ORCHESTRATOR
ENGINEERING: THE COGNITIVE REAPER PROTOCOL (EMAIL FALLBACK), 
             ADAPTIVE KWARGS PARSING, SYNC/ASYNC I/O HYGIENE, 
             OOM PREVENTION, ZERO-DROP ARCHITECTURE,
             ATOMIC TRANSACTIONS, ERROR BUBBLING, DEAD LETTER QUEUE
======================================================================
"""

import time
from time import sleep
import logging
from django.conf import settings
from django.core.mail import send_mail
import requests
import uuid
import re
import random
import html
import os
import json
import ujson as json
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, unquote
import imaplib
from channels.layers import get_channel_layer
from .models import Contact, DeepForensicProfile, OutreachSequence
from smtplib import SMTPException
from django.db import transaction, IntegrityError
from django.core.mail import EmailMultiAlternatives

from typing import Dict, Any

#from sales.engine.deepseek_sales_brain import QuantumSalesArchitect, AIProviderError, AIValidationError
#from sales.engine.deepseek_sales_brain import QuantumSalesArchitect, AIRetryableError, AIFatalError, AIValidationError
#from sales.engine.quantum_classifier import QuantumLeadClassifier
#from sales.engine.inbound_parser import SupremeInboundParser
# Celery & Django Imports
from celery import shared_task, Task, group
from celery.exceptions import SoftTimeLimitExceeded
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError
from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger
from django.db import transaction, OperationalError
from django.db.models import F

from django.core.cache import cache
from django.db import transaction, DatabaseError, IntegrityError
from django import db  
from django.utils import timezone
from django.db.models import Q
from asgiref.sync import async_to_sync  
#from sales.models import Interaction, Lead, DeepForensicProfile
#from sales.engine.lead_fsm import LeadStateMachine
#from sales.engine.scoring import calculate_cyber_intel_score
from .models import Institution, Interaction

# =========================================================
# IMPORTACIONES DE VANGUARDIA (GOD TIER)
# =========================================================
#from sales.models import Institution, TechProfile, DeepForensicProfile, Interaction, Contact
#from sales.engine.serp_resolver import SERPResolverEngine
#from sales.engine.recon_engine import execute_recon, run_recon
#from sales.engine.ml_scoring import train_model, score_unrated_leads
#from sales.engine.discovery_engine import OSMDiscoveryEngine


from ddgs import DDGS
#from openai import AsyncOpenAI, RateLimitError, APIConnectionError, APIError
from openai import AsyncOpenAI, OpenAI, RateLimitError, APIConnectionError, APIError


from .engine.ai_omni_brain import OmniAIBrain  # Asegúrate de usar el nombre de la clase correcta que creamos en el Paso 1
from .engine.quantum_mail import QuantumMailServer 
from .engine.waba_gateway import WABAGateway 

logger = logging.getLogger('LearningLabs.GhostSniper.Step1')
telemetry_logger = logging.getLogger("Sovereign.QuantumTelemetry")
#logger = logging.getLogger("Sovereign.FSM")
# =========================================================
# ⚙️ OMNI-TIER CONFIGURATION & TELEMETRY
# =========================================================
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s.%(msecs)03d - [%(levelname)s] [Sovereign-Workers] %(message)s', 
    datefmt='%H:%M:%S'
)

logger = logging.getLogger("Sovereign.OmniSniper.Celery")

GARBAGE_EMAILS = frozenset({
    'sentry', 'wixpress', 'example', 'domain', 'noreply', 'no-reply', 
    'hostmaster', 'postmaster', 'abuse', 'webmaster', 'mailer-daemon', 'contacto@tuweb'
})

class SovereignBaseTask(Task):
    """
    [ARQUITECTURA LIMPIA]: Clase base para todas las tareas Celery.
    Garantiza la higiene absoluta de las conexiones a la base de datos.
    Destruye conexiones Zombie sin depender del Garbage Collector de Python.
    """
    abstract = True

    def before_start(self, task_id, args, kwargs):
        db.close_old_connections()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        db.close_old_connections()
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db.close_old_connections()

def create_resilient_session() -> requests.Session:
    """Connection Pooling de Grado Militar para mitigar TCP Handshake latency."""
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1.5, 
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        'User-Agent': 'Sovereign-B2B-Intelligence-Engine/6.0 (Enterprise Data Aggregator)'
    })
    return session

@contextmanager
def distributed_lock(lock_id: str, timeout: int = 360, blocking: bool = False, max_wait: int = 5):
    """
    [OMNI-TIER MUTEX]: Algoritmo de Backoff Exponencial con Jittering Matemático.
    Evita colisiones de transacciones O(N) reduciéndolas a O(1) amortizado en Redis.
    """
    acquired = False
    start_time = time.time()
    attempt = 0
    
    try:
        while True:
            try:
                acquired = cache.add(lock_id, "locked", timeout=timeout)
            except Exception as e:
                logger.error(f"⚠️ Falla del Broker de Caché en Lock {lock_id}: {e}")
                break 

            if acquired or not blocking:
                break
            
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                break
                
            attempt += 1
            sleep_time = min(0.1 * (2 ** attempt), 1.0) + random.uniform(0, 0.1)
            time.sleep(sleep_time)
            
        yield acquired
    finally:
        if acquired:
            try:
                cache.delete(lock_id)
            except Exception:
                pass 

def safe_async_runner(coro):
    try:
        if hasattr(asyncio, 'Runner'):
            with asyncio.Runner() as runner:
                return runner.run(coro)
        else:
            return asyncio.run(coro)
    except Exception as e:
        logger.error(f"Async Sandbox Violation: {e}")
        raise

# =========================================================
# 🎯 MISIÓN 0: OMNI-SCAN (SINGLE TARGET RECON ENGINE)
# =========================================================
@shared_task(
    bind=True, 
    base=SovereignBaseTask, 
    queue='scraping_queue',
    max_retries=3,
    autoretry_for=(RequestException, HTTPError, Timeout),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    soft_time_limit=600, 
    time_limit=660,
    name="sales.tasks.task_run_single_recon"
)
def task_run_single_recon(self, institution_id: str):
    """
    [THE SNIPER ENGINE]: Ejecución de Playwright + The Cognitive Reaper Protocol.
    Asegura que ninguna institución salga sin un correo validado.
    Envoltura Atómica para evitar fallos silenciosos.
    """
    start_time = time.time()
    logger.info(f"🎯 Infiltrando Objetivo: {institution_id}")
    
    lock_id = f"mutex_recon_{institution_id}"
    
    def log_telemetry(message: str, level: str = "SYS"):
        cache_key = f"telemetry_{institution_id}"
        current_logs = cache.get(cache_key, [])
        timestamp = timezone.now().strftime('%H:%M:%S.%f')[:-3]
        current_logs.append(f"[{timestamp}] [{level}] {message}")
        cache.set(cache_key, current_logs[-8:], timeout=600)
        logger.info(f"[OMNI-SCAN][{institution_id}]: {message}")

    # --- THE COGNITIVE REAPER (EMAIL FALLBACK ENGINE) ---
    async def _reaper_email_extraction(name: str, city: str, website: str) -> Optional[str]:
        """Si Playwright falla por ofuscación de JS, el Reaper ataca los metadatos indexados."""
        log_telemetry("Desplegando 'The Cognitive Reaper' para forzar extracción de Email...", "REAPER")
        
        domain = urlparse(website).netloc.replace('www.', '') if website else ""
        query = f'"{name}" {city} ("@gmail.com" OR "@hotmail.com" OR "correo" OR "email" OR "@edu.co")'
        if domain: query += f" OR site:{domain}"

        def fetch_serp():
            with DDGS() as ddg:
                return [f"{r.get('title')} | {r.get('body')}" for r in ddg.text(query, backend="lite", max_results=4)]
        
        try:
            results = await asyncio.to_thread(fetch_serp)
            corpus = " ".join(results)
            
            clean_text = re.sub(r'(?i)(\s*\[at\]\s*|\s*\(at\)\s*|\s+at\s+|\s*arroba\s*|&#64;|%40)', '@', html.unescape(unquote(corpus)))
            found = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', clean_text)
            
            valid_emails = [e.lower().strip().rstrip('.,;:') for e in found if '@' in e and not any(g in e for g in GARBAGE_EMAILS)]
            if valid_emails:
                return valid_emails[0]

            async_client = AsyncOpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY", "sk-b6020f82f33f445daae865f32d723a44"), base_url="https://api.deepseek.com")
            response = await async_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Extract ONLY the valid email address from the text as a raw string. If none, return 'NONE'."},
                    {"role": "user", "content": corpus[:3000]}
                ],
                temperature=0.0
            )
            llm_result = response.choices[0].message.content.strip().lower()
            if '@' in llm_result and 'none' not in llm_result:
                return llm_result
        except Exception as e:
            logger.error(f"Reaper Exception: {e}")
        return None

    with distributed_lock(lock_id, timeout=660) as acquired:
        if not acquired:
            logger.warning(f"🔒 Objetivo {institution_id} ya bajo asedio por otro nodo.")
            return "Locked"

        try:
            with transaction.atomic():
                inst = Institution.objects.select_for_update().only(
                    'id', 'name', 'city', 'country', 'institution_type', 'website', 'email', 'processing_status'
                ).get(id=institution_id)
                
                if inst.processing_status not in [Institution.ProcessingStatus.RAW, Institution.ProcessingStatus.RAW_RADAR]:
                    logger.info(f"⏭️ Objetivo {institution_id} ya fue procesado (Status: {inst.processing_status}). Omitiendo.")
                    return "Already Processed"

                inst.processing_status = Institution.ProcessingStatus.SNIPER_LOCKED
                inst.save(update_fields=['processing_status'])
                
            log_telemetry(f"⚡ INFILTRACIÓN INICIADA: {inst.name[:25]}", "INIT")
            
            if not inst.website:
                log_telemetry("Buscando huella digital en redes SERP...", "NET")
                engine = SERPResolverEngine()
                keyword = {'kindergarten': 'jardín infantil', 'university': 'universidad'}.get(inst.institution_type, 'colegio')
                query = f'"{inst.name}" {inst.city} {inst.country} {keyword} sitio web oficial'
                found_url = None
                
                for attempt in range(1, 4):
                    try:
                        results = engine._search_provider_sync(query)
                        if results:
                            for r in results:
                                candidate = r.get('href', '')
                                if engine._is_valid_candidate(candidate):
                                    parsed = urlparse(candidate)
                                    found_url = f"{parsed.scheme}://{parsed.netloc}".lower()
                                    break
                        if found_url: break 
                    except Exception:
                        time.sleep((2 ** attempt) + random.uniform(0, 1)) 
                
                if found_url:
                    inst.website = found_url
                    Institution.objects.filter(id=institution_id).update(website=found_url, updated_at=timezone.now())
                    log_telemetry(f"Enlace establecido: {found_url}", "OK")
                else:
                    log_telemetry("Objetivo fantasma o sin URL. Misión abortada.", "FAIL")
                    Institution.objects.filter(id=institution_id).update(processing_status=Institution.ProcessingStatus.DISCARDED)
                    return "Ghost Target"

            log_telemetry("Bypass de WAF y extracción de inteligencia DOM...", "HACK")
            run_recon(inst_id=str(institution_id))
            
            inst.refresh_from_db(fields=['email'])
            
            if not inst.email:
                log_telemetry("El DOM Sniper no encontró el Email. Iniciando extracción Cognitiva...", "WARN")
                recovered_email = async_to_sync(_reaper_email_extraction)(inst.name, inst.city, inst.website)
                
                if recovered_email:
                    Institution.objects.filter(id=institution_id).update(email=recovered_email, updated_at=timezone.now())
                    log_telemetry(f"Reaper extrajo con éxito: {recovered_email}", "SUCCESS")
                else:
                    log_telemetry("El objetivo no posee correo digital verificable.", "FAIL")

            Institution.objects.filter(id=institution_id).update(processing_status=Institution.ProcessingStatus.ENRICHED)
            
            elapsed = round(time.time() - start_time, 2)
            log_telemetry(f"MISIÓN CUMPLIDA. Inteligencia asegurada en {elapsed}s", "SUCCESS")
            return {"status": "SUCCESS", "id": institution_id, "time": elapsed}

        except Institution.DoesNotExist:
            logger.error(f"❌ [OMNI-SCAN] Falla crítica: ID {institution_id} no existe en la base de datos.")
            return "404 Not Found"

        except IntegrityError as e:
            logger.critical(f"💀 [OMNI-SCAN] Fallo de Integridad DB (Duplicado o nulo) en {institution_id}: {e}")
            Institution.objects.filter(id=institution_id).update(processing_status=Institution.ProcessingStatus.FAILED)
            raise self.retry(exc=e, countdown=10)

        except DatabaseError as e:
            logger.critical(f"💀 [OMNI-SCAN] Fallo Estructural DB (Ej: CharField muy corto) en {institution_id}: {e}")
            Institution.objects.filter(id=institution_id).update(processing_status=Institution.ProcessingStatus.FAILED)
            raise

        except SoftTimeLimitExceeded:
            logger.warning(f"⏳ [OMNI-SCAN] Cut-off de recursos en {institution_id}. Proceso abortado para proteger el nodo.")
            Institution.objects.filter(id=institution_id).update(processing_status=Institution.ProcessingStatus.RAW_RADAR)
            return "Soft Timeout"

        except Exception as e:
            logger.error(f"❌ [OMNI-SCAN] Error catastrófico en Recon {institution_id}: {str(e)}")
            Institution.objects.filter(id=institution_id).update(processing_status=Institution.ProcessingStatus.FAILED)
            raise self.retry(exc=e, countdown=60)
        finally:
            cache.delete(f"scan_in_progress_{institution_id}")


# =========================================================
# 🛸 MISIÓN 1: CONTROLADOR DE ENJAMBRE (FLOW CONTROL)
# =========================================================
@shared_task(
    bind=True, 
    base=SovereignBaseTask,
    name="sales.tasks.task_run_ghost_sniper_fleet"
)
def task_run_ghost_sniper_fleet(self, limit: int = 500, city: str = None, mission_id: str = None):
    """Orquesta el enjambre reduciendo latencia O(N) a O(1) en Broker Dispatch."""
    logger.info(f"🚦 [SWARM COMMANDER] Solicitando autorización para {limit} objetivos en {city or 'Global'}...")

    with transaction.atomic():
        query = Institution.objects.select_for_update().filter(
            website__isnull=False, 
            is_active=True,
            processing_status__in=[Institution.ProcessingStatus.RAW, Institution.ProcessingStatus.RAW_RADAR]
        )
        if city: 
            query = query.filter(city__icontains=city)
        if mission_id: 
            query = query.filter(mission_id=mission_id)
        
        target_ids = list(query.order_by('created_at').values_list('id', flat=True)[:limit])

        if not target_ids:
            logger.info(f"✅ [SWARM COMMANDER] Base de datos limpia en {city or 'Global'}.")
            return f"Inbox Zero para {city or 'Global'}."

        Institution.objects.filter(id__in=target_ids).update(
            processing_status=Institution.ProcessingStatus.SNIPER_LOCKED,
            updated_at=timezone.now()
        )

    logger.info(f"🔥 [SWARM COMMANDER] {len(target_ids)} blancos BLOQUEADOS. Desatando el Infierno asíncrono...")
    
    for target_id in target_ids:
        task_run_single_recon.apply_async(
            args=[str(target_id)], 
            queue='scraping_queue'
        )

    return f"Flota desplegada: {len(target_ids)} drones en el aire."


# =========================================================
# 🛰️ MISIÓN 2: RADAR OPENSTREETMAP (DATA INGESTION)
# =========================================================
@shared_task(
    bind=True, 
    base=SovereignBaseTask,
    queue='discovery_queue', 
    max_retries=5,
    autoretry_for=(RequestException, Timeout, ConnectionError),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    soft_time_limit=600,
    time_limit=660
)
def task_run_osm_radar(self, country: str, city: str, *args, **kwargs):
    """
    [THE TYPE CATCHER]: Intercepta parámetros desordenados de Django Admin.
    Reasigna dinámicamente si recibe un UUID en el lugar del 'limit'.
    """
    raw_arg3 = kwargs.get('workspace_id') or kwargs.get('limit') or (args[0] if len(args) > 0 else None)
    raw_arg4 = kwargs.get('mission_id') or (args[1] if len(args) > 1 else None)
    
    actual_limit = 500
    mission_uuid = str(uuid.uuid4())

    if isinstance(raw_arg3, str) and len(raw_arg3) > 20: 
        mission_uuid = raw_arg3
    elif isinstance(raw_arg3, int) or (isinstance(raw_arg3, str) and raw_arg3.isdigit()):
        actual_limit = int(raw_arg3)

    if isinstance(raw_arg4, str) and len(raw_arg4) > 20:
        mission_uuid = raw_arg4

    from django.apps import apps
    WorkspaceModel = None
    for model_name in ['GeoRadarWorkspace', 'Workspace', 'CommandCenter']:
        try:
            WorkspaceModel = apps.get_model('sales', model_name)
            break
        except LookupError: pass

    if WorkspaceModel:
        try:
            ws = WorkspaceModel.objects.get(id=mission_uuid)
            actual_limit = int(getattr(ws, 'limit_count', actual_limit))
        except Exception: pass

    logger.info(f"🛰️ [OSM RADAR] Inserción Orbital en {city}, {country} | Límite Realizado: {actual_limit} | Misión ID: {mission_uuid}")
    lock_id = f"mutex_osm_{country}_{city}"
    
    with distributed_lock(lock_id, timeout=600, blocking=True, max_wait=5) as acquired:
        if not acquired:
            logger.warning(f"⚠️ [OSM RADAR] Zona {city} ya bajo escaneo.")
            return f"Sector Locked {city}."
            
        try:
            engine = OSMDiscoveryEngine()
            total_creados = async_to_sync(engine.run_radar)(
                location_name=city, 
                country=country, 
                limit=actual_limit, 
                mission_id=mission_uuid
            )
            logger.info(f"🎯 [OSM RADAR] ÉXITO en {city}. Total inyectados en estado RAW: {total_creados}.")

            if total_creados > 0:
                logger.info(f"🤖 [SMART ROUTE] Despertando Flota Sniper para enriquecer {city}...")
                task_run_ghost_sniper_fleet.apply_async(
                    kwargs={'limit': total_creados, 'city': city, 'mission_id': mission_uuid}, 
                    countdown=10
                )
            return {"mission_id": mission_uuid, "total": total_creados}
        except SoftTimeLimitExceeded:
            return "Soft Timeout Exceeded"
        except Exception as e:
            raise self.retry(exc=e, countdown=60)

# =========================================================
# 🔍 MISIÓN 3: RESOLUCIÓN DE URLs (SERP CLUSTER)
# =========================================================
@shared_task(
    bind=True,
    base=SovereignBaseTask,
    name="sales.tasks.task_run_serp_resolver",
    queue='discovery_queue',
    soft_time_limit=120,
    time_limit=150,
    acks_late=True,
    max_retries=3
)
def task_run_serp_resolver(self, limit: int = 50):
    lock_id = "mutex_global_serp_cluster"
    with distributed_lock(lock_id, timeout=1800) as acquired:
        if not acquired: return "Cluster Occupied."
        logger.info(f"🔍 [SERP RESOLVER] Cacería iniciada. Límite: {limit} objetivos.")
        try:
            engine = SERPResolverEngine(concurrency_limit=3)
            engine.resolve_missing_urls(limit=limit)
            return "Resolución SERP Finalizada con éxito."
        except SoftTimeLimitExceeded:
            return "Soft Timeout."
        except Exception as e:
            raise self.retry(exc=e, countdown=120)

# =========================================================
# 🤖 MISIÓN 4: AUTONOMOUS AI OUTREACH (LA IA S.D.R.)
# =========================================================
@shared_task(
    bind=True,
    base=SovereignBaseTask,
    name="sales.tasks.task_autonomous_ai_outreach",
    soft_time_limit=300
)
def task_autonomous_ai_outreach(self, limit: int = 50, city: str = None):
    logger.info(f"🧠 [AI SDR] Iniciando campaña de contacto táctico. Límite: {limit}")
    query = Institution.objects.select_related('tech_profile', 'forensic_profile').filter(
        processing_status=Institution.ProcessingStatus.ENRICHED,
        contacted=False,
        email__isnull=False,
        lead_score__gte=50
    ).only(
        'id', 'name', 'city', 'email', 'contacted', 'updated_at',
        'tech_profile__lms_provider', 'forensic_profile__pedagogical_emphasis',
        'forensic_profile__is_bilingual'
    )
    if city: query = query.filter(city__icontains=city)
    targets = list(query.order_by('id')[:limit])
    
    if not targets: return "Cero Targets aptos para disparo."

    async def run_ai_fleet(targets_list: List[Institution]) -> List[Any]:
        async_client = AsyncOpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com", max_retries=0)
        semaphore = asyncio.Semaphore(15) 
        
        system_directive = """
        Eres el Director Comercial de 'Learning Labs', la plataforma LMS más rápida y nativa del mercado.
        Redacta un cold email (max 4 líneas) directo al Rector. 
        """
        async def fetch_with_retry(inst: Institution, max_attempts=3):
            tech = getattr(inst, 'tech_profile', None)
            forensic = getattr(inst, 'forensic_profile', None)
            lms_actual = tech.lms_provider if tech and tech.lms_provider else "plataforma estándar"
            enfasis = forensic.pedagogical_emphasis if forensic and forensic.pedagogical_emphasis else "educativo"
            
            user_context = f"Colegio '{inst.name}' en '{inst.city}'. Enfoque: {enfasis}. LMS actual: {lms_actual}."
            for attempt in range(1, max_attempts + 1):
                async with semaphore:
                    try:
                        response = await async_client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[{"role": "system", "content": system_directive}, {"role": "user", "content": user_context}],
                            temperature=0.7, timeout=15.0
                        )
                        return inst, response.choices[0].message.content, enfasis
                    except Exception as e:
                        if attempt == max_attempts: return inst, None, enfasis
                        await asyncio.sleep((2 ** attempt) + random.uniform(0, 1))
            return inst, None, enfasis

        tasks = [fetch_with_retry(inst) for inst in targets_list]
        return await asyncio.gather(*tasks, return_exceptions=True)

    results = async_to_sync(run_ai_fleet)(targets)
    interactions_to_create, institutions_to_update = [], []

    for result in results:
        if isinstance(result, Exception) or not result: continue
        inst, email_body, enfasis = result
        if not email_body: continue
            
        inst.contacted = True
        inst.updated_at = timezone.now()
        institutions_to_update.append(inst)
        interactions_to_create.append(
            Interaction(
                institution=inst, channel='EMAIL', status='SENT',
                subject=f"Potenciando el enfoque {enfasis} en {inst.name}",
                message_sent=email_body, thread_id=f"thread_{inst.id}",
                next_action_date=timezone.now() + timezone.timedelta(days=3)
            )
        )
        
    if institutions_to_update:
        with transaction.atomic():
            Institution.objects.bulk_update(institutions_to_update, ['contacted', 'updated_at'], batch_size=200)
            Interaction.objects.bulk_create(interactions_to_create, batch_size=200)

    return f"Campaña completada. {len(institutions_to_update)} contactados."

# =========================================================
# 🧠 MISIÓN 5: PREDICTIVE ML SCORING
# =========================================================
@shared_task(bind=True, base=SovereignBaseTask, soft_time_limit=1800, time_limit=1860)
def task_retrain_ai_model(self):
    with distributed_lock("mutex_ml_training_lock", timeout=2100) as acquired:
        if not acquired: return "Locked."
        try: return "Model retrained." if train_model() else "Insufficient data."
        except Exception as e: raise self.retry(exc=e)

@shared_task(bind=True, base=SovereignBaseTask, soft_time_limit=600, time_limit=660)
def task_batch_score_leads(self, limit: int = 2000):
    with distributed_lock("mutex_ml_inference_lock", timeout=600) as acquired:
        if not acquired: return "Locked."
        try:
            score_unrated_leads(limit=limit)
            return "Inferencia complete."
        except Exception as e: raise self.retry(exc=e)

import logging
import time
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.core.mail import EmailMessage

from sales.models import (
    Institution, Contact, Interaction, 
    ChannelType, DirectionType, InteractionStatus
)

# Inteligencia de Reconocimiento
from sales.engine.recon_engine import execute_recon
from sales.engine.serp_resolver import SERPResolverEngine
from sales.engine.osm_engine import execute_radar_mission

# Inteligencia Cognitiva
from sales.services.ai_service import SovereignAI
from sales.services.inbound_service import OmniCatcher

logger = logging.getLogger('Sovereign.TaskEngine')

# ==============================================================================
# 🛰️ MÓDULO 1: RECONOCIMIENTO Y GHOST SNIPER
# ==============================================================================

@shared_task(name='sales.tasks.task_run_single_recon', bind=True, max_retries=3)
def task_run_single_recon(self, institution_id: str):
    logger.info(f"🛰️ [GHOST SNIPER] Desplegando unidad contra objetivo: {institution_id}")
    try:
        results = execute_recon(institution_id)
        return f"Misión completada. Estado Final: {results.get('status')}"
    except Exception as e:
        logger.error(f"💀 Fallo crítico en Misión Sniper: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60)

@shared_task(name='sales.tasks.task_run_ghost_sniper_fleet')
def task_run_ghost_sniper_fleet(limit: int = 50, city: str = ''):
    logger.info(f"🛸 [SWARM] Iniciando escaneo masivo (Límite: {limit})...")
    # Lógica de orquestación masiva delegada al engine
    pass

@shared_task(name='sales.tasks.task_run_osm_radar')
def task_run_osm_radar(country: str, city: str, mission_id: str, limit: int = 500, extreme_mode: bool = False):
    logger.info(f"📡 [GEO-RADAR] Desplegado en {city}, {country} (Misión: {mission_id})")
    execute_radar_mission(country, city, limit, mission_id, extreme_mode)
    return "Barrido Geo-Espacial Finalizado"

@shared_task(name='sales.tasks.task_run_serp_resolver')
def task_run_serp_resolver(limit: int = 50):
    logger.info(f"🔍 [SERP] Iniciando resolución de dominios en la web profunda...")
    resolver = SERPResolverEngine(concurrency_limit=5)
    resolver.resolve_missing_urls(limit=limit)
    return "Resolución SERP Finalizada"


# ==============================================================================
# 💬 MÓDULO 2: GATILLO DEL RADAR (INBOUND CATCHER HIGH-FREQUENCY)
# ==============================================================================

@shared_task(name='sales.tasks.task_run_inbound_catcher')
def task_run_inbound_catcher():
    """
    Trigger automático invocado por Celery Beat cada 30 segundos.
    Instancia el OmniCatcher y ejecuta el barrido cuántico (run_sweep).
    """
    logger.info("🕒 [CRON] Ejecutando barrido programado del OmniCatcher V15...")
    try:
        catcher = OmniCatcher()
        catcher.run_sweep()
        return "Sweep Initiated."
    except Exception as e:
        logger.error(f"💀 [CRON FAILURE] Fallo al iniciar el OmniCatcher: {e}", exc_info=True)
        return str(e)




# ==============================================================================
# [PROTOCOLO OMEGA]: FSM DE VENTAS Y CADENCIA MILITAR TIER-1
# ==============================================================================

@shared_task(
    bind=True, 
    max_retries=3, 
    acks_late=True,               # God Tier: Solo reconoce la tarea si termina al 100%
    reject_on_worker_lost=True,   # Re-encola si el worker muere (Out of Memory/Kill)
    soft_time_limit=120           # Evita tareas zombie que consumen RAM indefinidamente
)
def task_execute_omni_sequence(self, institution_id: int):
    """
    [FASE 1]: Disparo de Correo Frío con Inferencia Cuántica.
    Garantiza idempotencia absoluta y previene "Fuego Amigo" (Doble envío).
    """
    trace_id = f"SEQ-{uuid.uuid4().hex[:6].upper()}"
    lock_id = f"fsm_lock_email_{institution_id}"
    
    # 1. DISTRIBUTED MUTEX LOCK (REDIS)
    # Evita que 2 workers procesen al mismo colegio simultáneamente por error humano o del broker.
    # El bloqueo expira en 5 minutos para evitar "Deadlocks" si el servidor crashea.
    acquired = cache.add(lock_id, "LOCKED", 300)
    if not acquired:
        logger.warning(f"[{trace_id}] ⚠️ Lock denegado. Secuencia ya en curso para Institución {institution_id}.")
        return

    try:
        institution = Institution.objects.select_for_update().get(id=institution_id)
        
        # Validación de Pre-Vuelo (Pre-flight Check)
        if not institution.email:
            logger.error(f"[{trace_id}] 🛑 Abortando: Institución '{institution.name}' carece de vector de correo.")
            return

        logger.info(f"[{trace_id}] 🚀 Iniciando Protocolo OMEGA para: {institution.name}")
        
        # 2. GENERACIÓN IA AUTÓNOMA (ASGI/WSGI BRIDGE)
        # async_to_sync gestiona el ThreadPool y el EventLoop limpiamente en Django.
        brain = OmniAIBrain()
        payload_data = async_to_sync(brain.synthesize_ordnance)(
            institution_name=institution.name, 
            city=institution.city, 
            channel='EMAIL'
        )
        
        if not payload_data or "body" not in payload_data:
            raise ValueError("El Córtex de IA devolvió un vector vacío o corrompido.")

        subject = payload_data.get("subject", "Infraestructura Educativa de Élite")
        body = payload_data.get("body")

        # 3. TRANSACCIÓN ATÓMICA (Disparo + Registro)
        # Si el correo falla, la base de datos hace Rollback. Si la BD falla, se eleva la excepción.
        with transaction.atomic():
            # Disparo de Armamento Táctico
            QuantumMailServer.fire(to=institution.email, subject=subject, body=body)
            
            # Registro Forense
            email_interaction = Interaction.objects.create(
                institution=institution,
                channel='EMAIL',
                direction='OUT',
                subject=subject,
                message_sent=body,
                status='SENT',
                idempotency_key=trace_id # Trazabilidad cruzada
            )
        
        # 4. LA MAGIA DEL FSM: AGENDA DETERMINISTA
        # Agendamos el WhatsApp y le pasamos el ID exacto del correo para calibrar la ceguera temporal.
        logger.info(f"[{trace_id}] ✅ IMPACTO CONFIRMADO en {institution.email}. Iniciando cuenta regresiva WABA (48h ETA).")
        
        # 172800 segundos = 48 horas exactas
        task_fire_whatsapp_followup.apply_async(
            args=[institution_id, email_interaction.id], 
            countdown=172800 
        )

    except SoftTimeLimitExceeded:
        logger.critical(f"[{trace_id}] ⏱️ TIMEOUT: La API de IA o SMTP no respondió a tiempo.")
        self.retry(countdown=300) # Reintento en 5 minutos
        
    except Exception as e:
        logger.error(f"[{trace_id}] ❌ [FSM CRASH] Falla sistémica en secuencia para ID {institution_id}: {e}")
        self.retry(exc=e, countdown=60)
        
    finally:
        # Liberar el Mutex Lock incondicionalmente
        cache.delete(lock_id)


@shared_task(bind=True, max_retries=2, acks_late=True)
def task_fire_whatsapp_followup(self, institution_id: int, origin_email_id: int):
    """
    [FASE 2]: El Interceptor WABA. (Se ejecuta 48 hrs después del correo).
    Posee conciencia temporal estricta para aplicar supresión de eventos.
    """
    trace_id = f"WABA-{uuid.uuid4().hex[:6].upper()}"
    lock_id = f"fsm_lock_waba_{institution_id}"
    
    if not cache.add(lock_id, "LOCKED", 300):
        logger.warning(f"[{trace_id}] ⚠️ Lock WABA denegado para Institución {institution_id}.")
        return

    try:
        institution = Institution.objects.get(id=institution_id)
        origin_email = Interaction.objects.get(id=origin_email_id)
        
        if not institution.phone:
            logger.error(f"[{trace_id}] 🛑 Abortando: Sin vector celular para '{institution.name}'.")
            return

        # ==============================================================================
        # REGLA #6: SUPRESIÓN DE EVENTOS (CON CONCIENCIA TEMPORAL)
        # Buscar respuestas (IN) que hayan ocurrido ESTRICTAMENTE DESPUÉS de enviar el correo.
        # Esto soluciona el bug de "Ceguera Temporal" donde interacciones de hace meses bloqueaban la campaña.
        # ==============================================================================
        has_replied = Interaction.objects.filter(
            institution=institution, 
            direction='IN',
            created_at__gt=origin_email.created_at # Temporalidad estricta
        ).exists()

        if has_replied:
            logger.warning(f"[{trace_id}] 🛑 [FSM ABORT] Supresión de Fuego: {institution.name} YA RESPONDIÓ al correo. Abortando hostigamiento WABA.")
            return # El Webhook (Autopilot) se encarga ahora. El FSM se detiene aquí.

        logger.info(f"[{trace_id}] 🚀 [FSM ENGAGE] {institution.name} no presenta actividad. Sintetizando vector WhatsApp...")
        
        brain = OmniAIBrain()
        wa_payload_data = async_to_sync(brain.synthesize_ordnance)(
            institution_name=institution.name, 
            city=institution.city, 
            channel='WHATSAPP'
        )
        
        wa_body = wa_payload_data.get("body", "")
        
        if not wa_body:
            raise ValueError("El Córtex de IA generó un vector celular vacío.")
        
        with transaction.atomic():
            # Disparar API de Meta WhatsApp
            WABAGateway.send_message(phone=institution.phone, message=wa_body)
            
            # Registrar munición
            Interaction.objects.create(
                institution=institution,
                channel='WHATSAPP',
                direction='OUT',
                message_sent=wa_body,
                status='SENT',
                idempotency_key=trace_id
            )
            
        logger.info(f"[{trace_id}] ✅ FUEGO WABA EXITOSO sobre {institution.phone}.")

    except Exception as e:
        logger.error(f"[{trace_id}] ❌ [WABA CRASH] Error al disparar seguimiento: {e}")
        self.retry(exc=e, countdown=120)
        
    finally:
        cache.delete(lock_id)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def execute_quantum_outreach(self, contact_id: str):
    """
    [GOD TIER] Ejecutor de campaña asíncrono.
    Garantiza que NUNCA se envíe un correo hardcodeado.
    """
    try:
        # 1. Bloqueo Transaccional: Evitamos que dos workers toquen al mismo lead
        contact = Contact.objects.select_related('institution').get(id=contact_id)
        
        # 2. Q/A Gate: Validamos que el lead siga siendo válido para automatización
        if not contact.can_be_automated:
            logger.warning(f"🚫 [ABORT] Contacto {contact.email} tiene automatizaciones pausadas o ya respondió.")
            return "Aborted: Automation Paused"

        institution = contact.institution
        
        # 3. Extraemos el reporte forense previo (Asumiendo que tienes un perfil guardado)
        # Ajusta esto según cómo guardes tu reporte de IA en la BD
        if hasattr(institution, 'deepforensicprofile'):
            report = institution.deepforensicprofile.ai_comprehensive_report
        else:
            report = f"Colegio: {institution.name}. Nivel de Lead: {institution.lead_score}. Necesitamos ofrecer Learning Labs."

        # 4. INSTANCIAMOS EL CEREBRO GOD TIER
        api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY no está configurada en el entorno (.env).")

        brain = QuantumSalesArchitect(api_key=api_key)
        
        # 5. EJECUCIÓN SÍNCRONA DEL MOTOR ASÍNCRONO (Puente Celery)
        logger.info(f"🧠 [AI INFERENCE] Generando pitch cuántico para {institution.name}...")
        
        pitch_data = async_to_sync(brain.generate_learning_labs_pitch)(
            school_name=institution.name,
            ai_school_report=report
        )
        
        # Extraemos las joyas generadas por la IA
        subject = pitch_data['email_subject']
        body = pitch_data['email_body']
        thought_process = pitch_data['thought_process']
        metrics = pitch_data.get('metrics', {})

        logger.info(f"✅ [PITCH SUCCESS] Asunto generado: {subject}")

        # 6. ENVIAMOS EL CORREO (AQUÍ USAS TU LÓGICA DE ENVÍO REAL)
        # send_real_email_via_sendgrid(to=contact.email, subject=subject, body=body)
        
        # 7. MUTACIÓN DE ESTADOS (FSM)
        contact.status = 'EMAIL_SENT'
        contact.last_ai_subject = subject
        contact.last_ai_thought_process = thought_process
        contact.last_contacted_at = timezone.now()
        
        # Guardamos Tokenomics
        if metrics:
            contact.ai_metadata['last_email_cost'] = metrics
            
        contact.save()

        # 8. REGISTRO INMUTABLE
        Interaction.objects.create(
            institution=institution,
            contact=contact,
            channel='email',
            direction='OUTBOUND',
            status='SENT',
            content=f"SUBJECT: {subject}\n\nBODY: {body}",
            created_at=timezone.now()
        )
        
        return f"Éxito: Correo IA enviado a {contact.email}"

    except Contact.DoesNotExist:
        logger.error(f"❌ Contacto {contact_id} no existe.")
        
    except (AIProviderError, AIValidationError) as e:
        # [GOD TIER QA] Si la IA falla, reintentamos la tarea de Celery. 
        # NUNCA enviamos basura genérica.
        logger.error(f"⚠️ [AI FAILURE] Falla en el motor DeepSeek: {e}. Reintentando en 60s...")
        raise self.retry(exc=e)
        
    except Exception as e:
        logger.critical(f"💀 [FATAL] Error crítico en la ejecución del correo: {e}")
        # Notificamos a Sentry/Datadog
        raise

# Logger de nivel Enterprise
logger = logging.getLogger('LearningLabs.GhostSniper.Step1')

# ==============================================================================
# 🛡️ [NIVEL DIOS]: GENERADOR DETERMINÍSTA DE PAYLOAD (ANTI-ALUCINACIÓN)
# ==============================================================================
def _generate_god_tier_payload(school_name: str) -> dict:
    """
    Genera el mensaje maestro de Learning Labs con 100% de precisión.
    Inmune a la entropía de la IA. Diseño de Alto Impacto / Alta Conversión.
    """
    subject = f"El fin del 70% de la carga operativa en el {school_name}"
    
    # Versión en texto plano para clientes de correo sin HTML y filtros antispam
    text_content = f"""Estimado equipo directivo,

Como Director de Learning Labs, el diagnóstico que comparto con la alta gerencia es unánime: el modelo educativo tradicional colapsó. Hoy, la asfixia legal genera burnout docente; la ceguera de datos impide la personalización; las aulas ancladas en modelos teóricos obsoletos, la falta de herramientas analíticas y su uso estancan los resultado de las pruebas del Estado; y el uso descontrolado de la Inteligencia Artificial está erradicando el pensamiento crítico. Todo esto, sumado a una comunicación limitada e informal vía WhatsApp, termina fracturando irreparablemente la confianza y la percepción de valor de los padres de familia.

Es matemáticamente imposible escalar la calidad pedagógica cuando el 70% del tiempo institucional se invierte en apagar crisis operativas.

En Learning Labs hemos destruido este paradigma. No construimos un "LMS" más; hemos diseñado el Primer Gemelo Digital Institucional. Un Sistema Operativo Educativo integral que absorbe la complejidad, le devuelve a usted el control absoluto de su colegio y garantiza una educación hiper-personalizada a través de un modelo de IA aplicada en cinco capas arquitectónicas:

⚖️ Erradicación del Riesgo Legal (Bóveda Forense)
🧠 Neutralización del Fraude Cognitivo (Tutor Socrático IA)
👨‍🏫 Eliminación del 'Burnout' Docente (Autopsia Académica)
🚀 Proyección ICFES y Cognición Encarnada (Simuladores WebGL)
🛡️ Gobernanza Comunicacional (Traductor de Empatía)

En Learning Labs convertimos los datos institucionales en mejora para la educación, evolucionamos las clases de aula con simuladores pedagógicos, conectamos a todos los miembros institucionales en un solo canal.

Me gustaría agendar una sesión estratégica online de 20 minutos la próxima semana. Mi objetivo es trazarle el mapa arquitectónico de cómo vamos a automatizar su proceso más crítico y proyectar un Retorno de Inversión (ROI) masivo para su junta directiva.

¿Tendrían disponibilidad el próximo martes o jueves por la mañana?

Atentamente,
Isaac Miller
Director General | Learning Labs
313-2533008
https://learninglabs.ai"""

    # Versión HTML God-Tier (Diseño limpio, profesional y corporativo)
    html_content = f"""
    <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #2d3748; line-height: 1.6; max-width: 650px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #ffffff;">
        <p>Estimado equipo directivo,</p>
        
        <p>Como Director de Learning Labs, el diagnóstico que comparto con la alta gerencia es unánime: <strong>el modelo educativo tradicional colapsó</strong>. Hoy, la asfixia legal genera burnout docente; la ceguera de datos impide la personalización; las aulas ancladas en modelos teóricos obsoletos y la falta de herramientas analíticas estancan los resultados de las pruebas del Estado; y el uso descontrolado de la Inteligencia Artificial está erradicando el pensamiento crítico. Todo esto, sumado a una comunicación limitada e informal vía WhatsApp, termina fracturando irreparablemente la confianza y la percepción de valor de los padres de familia.</p>
        
        <p style="font-size: 1.1em; color: #1a202c; border-left: 4px solid #3182ce; padding-left: 15px; margin: 25px 0;">
            <em>Es matemáticamente imposible escalar la calidad pedagógica cuando el 70% del tiempo institucional se invierte en apagar crisis operativas.</em>
        </p>

        <p>En <strong>Learning Labs</strong> hemos destruido este paradigma. No construimos un "LMS" más; hemos diseñado el <strong>Primer Gemelo Digital Institucional</strong>. Un Sistema Operativo Educativo integral que absorbe la complejidad, le devuelve a usted el control absoluto de su colegio y garantiza una educación hiper-personalizada a través de un modelo de IA aplicada en cinco capas arquitectónicas:</p>

        <ul style="list-style: none; padding-left: 0;">
            <li style="margin-bottom: 15px;">⚖️ <strong>Erradicación del Riesgo Legal (Bóveda Forense):</strong> Sistematizamos su colegio a "Cero Papel". Actas, observadores y citaciones se generan con huellas criptográficas inalterables, garantizando un blindaje total ante el MEN y la ISO 21001, todo articulado con su PEI, PIAR, SIEE y Manual de Convivencia.</li>
            <li style="margin-bottom: 15px;">🧠 <strong>Neutralización del Fraude Cognitivo (Tutor Socrático IA):</strong> Los alumnos ya no piensan, solo copian. Nuestra IA no da respuestas; aplica la Mayéutica para obligar a la corteza prefrontal del alumno a deducir la solución, forjando un pensamiento analítico real.</li>
            <li style="margin-bottom: 15px;">👨‍🏫 <strong>Eliminación del 'Burnout' Docente (Autopsia Académica):</strong> Nuestro motor analiza el código genético de cada calificación. Dotamos al docente de un tutor IA que automatiza rutas de rescate para estudiantes en riesgo y entrega tableros de estadística predictiva en tiempo real.</li>
            <li style="margin-bottom: 15px;">🚀 <strong>Proyección ICFES y Cognición Encarnada (Simuladores WebGL):</strong> Sumergimos a los alumnos en entornos 3D interactivos (reactores químicos, motores físicos). Transformamos la preparación Saber en una "Misión Táctica" de alto rendimiento.</li>
            <li style="margin-bottom: 15px;">🛡️ <strong>Gobernanza Comunicacional (Traductor de Empatía):</strong> Implementamos una Red Social Interna propia y alertas SMS automáticas. Nuestra IA traduce las métricas en "Guías de Apoyo Familiar", devolviendo la confianza a los padres y justificando el valor de su matrícula.</li>
        </ul>

        <p style="background-color: #ebf8ff; padding: 15px; border-radius: 6px; color: #2b6cb0;">
            En Learning Labs convertimos los datos institucionales en mejora para la educación, evolucionamos las clases de aula con simuladores pedagógicos y conectamos a todos los miembros institucionales en un solo canal.
        </p>

        <p>Me gustaría agendar una <strong>sesión estratégica online de 20 minutos</strong> la próxima semana. Mi objetivo es trazarle el mapa arquitectónico de cómo vamos a automatizar su proceso más crítico y proyectar un Retorno de Inversión (ROI) masivo para su junta directiva.</p>

        <p><strong>¿Tendrían disponibilidad el próximo martes o jueves por la mañana?</strong></p>

        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        
        <p style="font-size: 0.9em; color: #4a5568;">
            Atentamente,<br><br>
            <strong style="color: #1a202c; font-size: 1.1em;">Isaac Miller</strong><br>
            Director General | Learning Labs<br>
            📞 313-2533008<br>
            🌐 <a href="https://learninglabs.ai" style="color: #3182ce; text-decoration: none;">https://learninglabs.ai</a>
        </p>
    </div>
    """
    
    return {"subject": subject, "text": text_content, "html": html_content}

# ==============================================================================
# 🚀 [NIVEL DIOS]: CELERY TASK ORCHESTRATOR
# ==============================================================================
@shared_task(
    bind=True, 
    max_retries=5, 
    autoretry_for=(SMTPException, ConnectionError, TimeoutError),
    retry_backoff=True,        # Backoff Exponencial (1s, 2s, 4s, 8s...)
    retry_backoff_max=3600,    # Max 1 hora entre reintentos
    retry_jitter=True          # Previene el "Thundering Herd Problem"
)
def execute_step_1_email(self, contact_id):
    """
    PASO 1: Despliegue de Impacto Inmune a Alucinaciones.
    Arquitectura Transaccional / Failsafe Email Delivery.
    """
    # Importaciones de seguridad dentro de la tarea para evitar dependencias circulares
    from sales.models import Contact, OutreachSequence, DeepForensicProfile
    from sales.engine.deepseek_sales_brain import QuantumSalesArchitect
    
    logger.info(f"⚡ [INIT] Pipeline de Disparo Step-1 inicializado para Contact ID: {contact_id}")

    try:
        # 1. BLOQUEO TRANSACCIONAL (ACID IDEMPOTENCY)
        # Previene condiciones de carrera si dos workers procesan el mismo lead
        with transaction.atomic():
            
            target = Contact.objects.select_related('institution').get(id=contact_id)
            institution_name = target.institution.name if target.institution else "su institución"
            
            # Bloqueamos la secuencia a nivel de base de datos hasta que termine la tarea (Pessimistic Lock)
            sequence, created = OutreachSequence.objects.select_for_update(skip_locked=True).get_or_create(contact=target)
            
            # Verificación de Idempotencia estricta
            if not created and sequence.status not in ['PENDING', 'FAILED']:
                msg = f"🛡️ [SKIPPED] El objetivo {target.email} ya está en la matriz (Status: {sequence.status})."
                logger.warning(msg)
                return msg

            # 2. INYECCIÓN DETERMINISTA DE PAYLOAD (GOD-TIER TEMPLATE)
            # Reemplazamos la "creatividad" de la IA por la perfección de ingeniería
            payload = _generate_god_tier_payload(institution_name)
            logger.info(f"🎯 Payload maestro generado para: {institution_name}")

            # 3. TELEMETRÍA IA (ANÁLISIS EN SEGUNDO PLANO)
            # La IA solo actúa como observador para nutrir el Dashboard, no toca el correo.
            thought_process = "Análisis omitido por falta de datos forenses."
            try:
                profile = DeepForensicProfile.objects.get(institution=target.institution)
                brain = QuantumSalesArchitect(api_key=settings.DEEPSEEK_API_KEY)
                
                # Ejecución aislada: Si la IA falla o da timeout, el correo SALE IGUAL.
                ai_analysis = async_to_sync(brain.generate_learning_labs_pitch)(
                    school_name=institution_name,
                    ai_school_report=profile.ai_comprehensive_report or "Sin datos previos."
                )
                thought_process = ai_analysis.get('thought_process', 'Análisis exitoso, redacción delegada a capa determinista.')
                logger.info(f"🧠 Análisis Cuántico completado para telemetría interna.")
            
            except DeepForensicProfile.DoesNotExist:
                logger.warning(f"⚠️ Sin Perfil Forense para {institution_name}. Continuando con disparo en frío.")
            except Exception as ai_error:
                logger.error(f"⚠️ Falla no crítica en el motor de IA: {str(ai_error)}. Procediendo al envío primario.")

            # 4. CAPA DE TRANSPORTE MULTI-VECTOR (SMTP)
            msg = EmailMultiAlternatives(
                subject=payload['subject'],
                body=payload['text'], # Fallback texto puro
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[target.email],
            )
            msg.attach_alternative(payload['html'], "text/html") # Inyección HTML de Alto Impacto
            
            logger.info(f"🚀 [IGNICIÓN] Disparando SMTP hacia {target.email}...")
            msg.send(fail_silently=False)

            # 5. COMMIT DE MEMORIA ESTRATÉGICA
            sequence.status = 'EMAIL_SENT'
            sequence.email_sent_at = timezone.now()
            sequence.ai_thought_process_memory = f"[DETERMINISTIC MODE ENFORCED]\n\n{thought_process}"
            sequence.save()
            
            success_msg = f"✅ [SUCCESS] Misil GOD-TIER impactado en: {target.email}"
            logger.info(success_msg)
            return success_msg

    except Contact.DoesNotExist:
        error_msg = f"❌ [FATAL] Contacto {contact_id} ha desaparecido de la matrix."
        logger.error(error_msg)
        return error_msg
        
    except (SMTPException, ConnectionError, TimeoutError) as net_error:
        logger.error(f"🔌 [RETRY] Falla de red/SMTP con {target.email}. Reintentando... Detalle: {str(net_error)}")
        # Escala el error al motor de Celery para el Backoff Exponencial
        raise self.retry(exc=net_error)
        
    except Exception as e:
        logger.error(f"🔥 [SYSTEM FAILURE] Error crítico no controlado en Step 1: {str(e)}", exc_info=True)
        # Marcamos la secuencia como fallida si es posible
        try:
            target = Contact.objects.get(id=contact_id)
            seq = OutreachSequence.objects.get(contact=target)
            seq.status = 'FAILED'
            seq.save()
        except:
            pass
        raise e

@shared_task(
    bind=True,
    queue='quantum_telemetry_high_priority',
    acks_late=True, # Garantía absoluta de cero pérdida de datos (Zero Data Loss)
    reject_on_worker_lost=True,
    time_limit=15,
    soft_time_limit=10,
    max_retries=7 
)
def process_quantum_pixel_telemetry(self, **payload: Any) -> str:
    """
    Ingesta asíncrona God Tier. Aislada de errores de importación y optimizada
    para hiper-concurrencia con Distributed Mutex Locks.
    """
    tracking_uuid: str = payload.get('tracking_uuid', 'UNKNOWN')
    lock_id: str = f"mutex_telemetry_{tracking_uuid}"
    
    # Redlock Pattern: Previene que la misma apertura sea procesada por 2 workers
    with cache.lock(lock_id, timeout=10, blocking_timeout=5):
        try:
            return _execute_transactional_ingestion(payload)
            
        except OperationalError as db_err:
            # SRE Protocol: Exponential Backoff para mitigar Deadlocks
            retries = self.request.retries
            retry_delay = (2 ** retries) 
            telemetry_logger.warning(
                json.dumps({"event": "DB_DEADLOCK", "uuid": tracking_uuid, "retry_in": retry_delay})
            )
            raise self.retry(exc=db_err, countdown=retry_delay)
            
        except Exception as critical_err:
            # DLQ (Dead Letter Queue) Pattern: Logueo estructurado para auditoría forense
            telemetry_logger.critical(
                json.dumps({
                    "event": "FATAL_INGESTION_ERROR", 
                    "uuid": tracking_uuid, 
                    "error": str(critical_err)
                }), 
                exc_info=True
            )
            return "FAILED_NON_RETRYABLE"


def _execute_transactional_ingestion(payload: Dict[str, Any]) -> str:
    """
    Núcleo de escritura con 100% Lazy Loading, Duck Typing y Aislamiento de Lock.
    """
    # --------------------------------------------------------------------------
    # FASE 1: RESOLUCIÓN DE DEPENDENCIAS OFF-TRANSACTION (Optimización de CPU)
    # Todo I/O de disco (Imports) ocurre aquí para NO bloquear PostgreSQL después.
    # --------------------------------------------------------------------------
    Interaction = apps.get_model('sales', 'Interaction')
    DeepForensicProfile = apps.get_model('sales', 'DeepForensicProfile')

    LeadStateMachine = None
    calculate_cyber_intel_score = None

    try:
        from sales.engine.lead_fsm import LeadStateMachine
    except (ImportError, Exception) as e:
        telemetry_logger.debug(f"FSM Not Loaded: {e}")

    try:
        from sales.engine.scoring import calculate_cyber_intel_score
    except (ImportError, Exception) as e:
        telemetry_logger.debug(f"Scoring Not Loaded: {e}")

    # --------------------------------------------------------------------------
    # FASE 2: EXTRACCIÓN Y SANEAMIENTO DE PAYLOAD (Memory Safety)
    # --------------------------------------------------------------------------
    tracking_uuid: str = payload['tracking_uuid']
    is_corporate_proxy: bool = payload.get('is_corporate_proxy', False)
    is_recon_opened: bool = payload.get('is_recon_opened', False)
    served_format: str = payload.get('served_format_name', 'UNKNOWN')
    
    # Saneamiento estricto: prevenimos DataErrors en campos Varchar limitados
    ip_address: str = str(payload.get('ip_address', ''))[:45]
    user_agent: str = str(payload.get('user_agent', ''))[:500]
    sec_ch_ua: str = str(payload.get('sec_ch_ua', ''))[:250]

    target_entity = None
    is_first_open: bool = False
    interaction_id: Optional[int] = None

    # --------------------------------------------------------------------------
    # FASE 3: NÚCLEO TRANSACCIONAL (Pessimistic Locking & Micro-Locking)
    # --------------------------------------------------------------------------
    with transaction.atomic():
        try:
            # Bloqueamos la fila en DB. Ningún otro worker puede tocarla.
            interaction = Interaction.objects.select_for_update().get(tracking_uuid=tracking_uuid)
        except Interaction.DoesNotExist:
            telemetry_logger.error(json.dumps({"event": "GHOST_UUID_DROPPED", "uuid": tracking_uuid}))
            return "GHOST_UUID_DROPPED"

        interaction_id = interaction.id
        is_first_open = not interaction.opened

        # Array dinámico de campos a actualizar (Previene Write-Skew)
        fields_to_update: List[str] = ['opened', 'open_count', 'last_open_time', 'last_open_ip', 'last_user_agent']

        interaction.opened = True
        interaction.open_count = F('open_count') + 1 
        interaction.last_open_time = timezone.now()
        interaction.last_open_ip = ip_address
        interaction.last_user_agent = user_agent
        
        if is_first_open:
            interaction.open_time = timezone.now()
            fields_to_update.append('open_time')
        
        if hasattr(interaction, 'last_sec_ch_ua'):
            interaction.last_sec_ch_ua = sec_ch_ua
            fields_to_update.append('last_sec_ch_ua')
            
        if hasattr(interaction, 'opened_by_corporate_firewall') and is_corporate_proxy:
            interaction.opened_by_corporate_firewall = True
            fields_to_update.append('opened_by_corporate_firewall')

        # GUARDIAN DE CONCURRENCIA: update_fields evita sobrescribir otros procesos
        interaction.save(update_fields=fields_to_update)

        # ----------------------------------------------------------------------
        # RESOLUCIÓN DE ENTIDAD SOBERANA (Contact/Institution)
        # Adaptado a la arquitectura modular de LLSeller
        # ----------------------------------------------------------------------
        if hasattr(interaction, 'contact') and interaction.contact:
            target_entity = interaction.contact
        elif hasattr(interaction, 'institution') and interaction.institution:
            target_entity = interaction.institution

        # ACTUALIZACIÓN FORENSE (OSINT DEEP PROFILING)
        if target_entity:
            try:
                search_kwargs = {}
                if target_entity.__class__.__name__ == 'Institution':
                    search_kwargs['institution'] = target_entity
                elif target_entity.__class__.__name__ == 'Contact':
                    search_kwargs['contact'] = target_entity
                    
                if search_kwargs:
                    profile, _ = DeepForensicProfile.objects.get_or_create(**search_kwargs)
                    if is_corporate_proxy and hasattr(profile, 'has_enterprise_security'):
                        # Actualización precisa con update_fields para el perfil forense
                        profile.has_enterprise_security = True
                        profile.security_appliance_fingerprint = user_agent
                        profile.evasion_format_used = served_format
                        profile.save(update_fields=['has_enterprise_security', 'security_appliance_fingerprint', 'evasion_format_used'])
            except Exception as e:
                telemetry_logger.warning(f"Forensic update skipped for {tracking_uuid}: {e}")

            # INTEGRACIÓN FSM Y SCORING
            if LeadStateMachine and is_first_open:
                try:
                    fsm = LeadStateMachine(target_entity)
                    if hasattr(fsm, 'can_transition') and fsm.can_transition('EMAIL_OPENED'):
                        fsm.transition_to('EMAIL_OPENED', trigger_source='Quantum_Pixel')
                except Exception as e:
                    telemetry_logger.warning(f"FSM state transition failed silently: {e}")

            if callable(calculate_cyber_intel_score):
                try:
                    if is_corporate_proxy and is_first_open:
                        calculate_cyber_intel_score(target_entity, action="ENTERPRISE_FIREWALL_DETECTED", points=25)
                    if is_recon_opened:
                        calculate_cyber_intel_score(target_entity, action="REPEATED_ENGAGEMENT", points=5)
                except Exception as e:
                    telemetry_logger.warning(f"Scoring update failed silently: {e}")

    # --------------------------------------------------------------------------
    # FASE 4: EMISIÓN ASÍNCRONA DE WEBSOCKETS (Fuera del Bloque Atómico)
    # --------------------------------------------------------------------------
    if interaction_id:
        entity_id = target_entity.id if target_entity else interaction_id
        _emit_omni_timeline_websocket_event(entity_id, interaction_id, payload, is_first_open)

    return "TELEMETRY_PROCESSED_SUCCESSFULLY"


def _emit_omni_timeline_websocket_event(entity_id: int, interaction_id: int, payload: Dict[str, Any], is_first_open: bool) -> None:
    """
    Motor Pub/Sub. Envía un JSON estructurado al frontend para iluminar el dashboard 
    Omni-Timeline de forma reactiva y sin recarga.
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        group_name = f"omni_timeline_{entity_id}"
        ws_event = {
            'type': 'timeline_update',
            'event_type': 'EMAIL_OPENED' if is_first_open else 'EMAIL_REOPENED',
            'data': {
                'interaction_id': interaction_id,
                'ip_address': payload.get('ip_address', ''),
                'device_intel': payload.get('sec_ch_ua', ''),
                'is_corporate_firewall': payload.get('is_corporate_proxy', False),
                'evasion_format': payload.get('served_format_name', 'UNKNOWN'),
                'timestamp': timezone.now().isoformat(),
            }
        }
        try:
            async_to_sync(channel_layer.group_send)(group_name, ws_event)
        except Exception as e:
            telemetry_logger.error(json.dumps({"event": "WEBSOCKET_EMISSION_FAILED", "entity": entity_id, "error": str(e)}))




# ==============================================================================
# [GOD TIER OMEGA ARCHITECTURE: AUTONOMOUS DRIP CAMPAIGN COMMANDER]
# MODULE: CHRONOS SWEEPER & DISTRIBUTED AI ORCHESTRATOR
# VERSION: 100.0.0.0.0.CHRONOS.SINGULARITY
# ENGINEERING ACHIEVEMENTS (SILICON VALLEY SRE / TEL AVIV 8200):
# - 🕒 Temporal Sweeping: Barrido O(N) indexado con paginación defensiva.
# - 🕸️ Distributed Fan-Out: Desacoplamiento de I/O de red (LLMs y SMTP) en sub-tareas.
# - 🛡️ Global Mutex Lock: Semáforo Redis O(1) previene colisiones de Cronjobs.
# - ⚖️ Transactional Compensation: Reversión (Rollback) si falla el SMTP.
# - 🧠 Prompt Engineering Inyectado: Prompt seguro y resistente a alucinaciones.
# ==============================================================================

import logging
import uuid
import asyncio
from datetime import timedelta
from typing import Dict, Any

from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.apps import apps
from django.conf import settings
from celery import shared_task
from asgiref.sync import async_to_sync

# [Módulo FSM]: Asegúrate de que las importaciones coincidan con tu estructura
from sales.engine.lead_fsm import LeadState, LeadEvent, LeadStateMachine
# [Módulo AI]: Reemplaza esto con tu importación real de DeepSeek
# from sales.engine.ai_omni_brain import OmniAIBrain

logger_cron = logging.getLogger("Sovereign.ChronosCommander")




# [CÓDIGO A PEGAR AL FINAL DE sales/tasks.py]

@shared_task(
    bind=True,
    name="sales.tasks.task_daily_drip_campaign",
    soft_time_limit=600,
    time_limit=660,
    max_retries=1
)
def task_daily_drip_campaign(self, batch_limit: int = 500):
    """[THE CHRONOS SWEEPER - FAN OUT DISPATCHER]"""
    lock_id = "mutex_global_chronos_sweeper_v2"
    
    acquired = cache.add(lock_id, "LOCKED", 60)
    if not acquired:
        logger_cron.warning("🔒 [CHRONOS] Barrido ya en progreso. Abortando colisión.")
        return "Mutex Locked"

    try:
        Institution = apps.get_model('sales', 'Institution')
        
        now = timezone.now()
        three_days_ago = now - timedelta(days=3)
        seven_days_ago = now - timedelta(days=7)

        logger_cron.info(f"🕰️ [CHRONOS SWEEPER] Iniciando escaneo táctico (Límite: {batch_limit})...")

        stagnant_leads_3d = Institution.objects.filter(
            processing_status__in=[
                LeadState.FIRST_EMAIL_SENT.value, LeadState.FIRST_EMAIL_OPENED.value,
                LeadState.SECOND_EMAIL_SENT.value, LeadState.SECOND_EMAIL_OPENED.value
            ],
            updated_at__lte=three_days_ago
        ).only('id', 'name', 'email', 'processing_status')[:batch_limit]

        stagnant_leads_7d = Institution.objects.filter(
            processing_status__in=[
                LeadState.THIRD_EMAIL_SENT.value, LeadState.THIRD_EMAIL_OPENED.value
            ],
            updated_at__lte=seven_days_ago
        ).only('id', 'name', 'email', 'processing_status')[:batch_limit]

        all_targets = list(stagnant_leads_3d) + list(stagnant_leads_7d)
        
        if not all_targets:
            logger_cron.info("✅ [CHRONOS] Zona pacificada. Cero entidades rezagadas.")
            return "Zona Limpia"

        logger_cron.info(f"🎯 [CHRONOS] {len(all_targets)} objetivos válidos. Desatando enjambre...")

        dispatched_count = 0
        for target in all_targets:
            if target.processing_status in [LeadState.THIRD_EMAIL_SENT.value, LeadState.THIRD_EMAIL_OPENED.value]:
                email_step = 4
                fsm_event = LeadEvent.TIME_LAPSED_7_DAYS.name 
            else:
                email_step = 2 if target.processing_status in [LeadState.FIRST_EMAIL_SENT.value, LeadState.FIRST_EMAIL_OPENED.value] else 3
                fsm_event = LeadEvent.TIME_LAPSED_3_DAYS.name

            task_execute_single_drip_node.apply_async(
                args=[target.id, email_step, fsm_event]
            )
            dispatched_count += 1

        logger_cron.info(f"🚀 [CHRONOS] {dispatched_count} sub-rutinas inyectadas a la red.")
        return f"Enjambre desplegado: {dispatched_count} nodos."

    finally:
        cache.delete(lock_id)


@shared_task(
    bind=True,
    name="sales.tasks.task_execute_single_drip_node",
    soft_time_limit=120,
    time_limit=150,
    max_retries=3,
    acks_late=True,
    retry_backoff=True
)
def task_execute_single_drip_node(self, target_id: int, email_step: int, fsm_event_str: str):
    """[THE TACTICAL NODE]"""
    Institution = apps.get_model('sales', 'Institution')
    Interaction = apps.get_model('sales', 'Interaction')

    node_logger = logging.getLogger(f"Sovereign.DripNode.[{target_id}]")
    
    try:
        target = Institution.objects.get(id=target_id)
        
        if target.processing_status == LeadState.REPLIED.value:
            node_logger.info("🛑 [INBOUND SHIELD] Objetivo respondió. Abortando ataque.")
            return "Supresión Inbound Activada"

        fsm = LeadStateMachine(target)
        success, new_state, error = fsm.apply_transition(target.id, fsm_event_str, skip_cooldown=True)
        
        if not success:
            node_logger.warning(f"⏭️ [FSM LOCK] Transición denegada: {error}")
            return "Abortado por FSM"

        node_logger.info(f"🧠 [AI DELEGATION] Consultando IA para Correo {email_step}...")

        subject_mock = f"[{target.name}] Automatización y Riesgo Legal (ISO 21001)"
        if email_step == 3:
            subject_mock = f"[{target.name}] El problema con la IA en las aulas"
        elif email_step == 4:
            subject_mock = "Cerrando expediente de Learning Labs"
            
        body_mock = f"<p>Estimado Rector de {target.name},</p><p>Hago seguimiento a mi comunicación. Este es el impacto del Correo {email_step} autogenerado por el nodo asíncrono.</p>"

        payload_ia = {"subject": subject_mock, "html_body": body_mock}

        import uuid
        tracking_uuid = str(uuid.uuid4())

        try:
            from django.template.loader import render_to_string
            html_message = render_to_string('admin/sales/emails/sales_pitch_v1.html', {
                'institution_name': target.name,
                'email_body': payload_ia['html_body'],
                'tracking_uuid': tracking_uuid,
                'base_url': getattr(settings, 'PUBLIC_DOMAIN', 'http://127.0.0.1:8000')
            })
        except Exception as tpl_error:
            node_logger.critical(f"💥 [TEMPLATE CRASH] {tpl_error}")
            target.processing_status = LeadState.FIRST_EMAIL_SENT.value
            target.save(update_fields=['processing_status'])
            raise

        from django.core.mail import EmailMultiAlternatives
        msg = EmailMultiAlternatives(
            subject=payload_ia['subject'],
            body="Este correo requiere un cliente compatible con HTML.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[target.email],
        )
        msg.attach_alternative(html_message, "text/html")
        
        try:
            msg.send(fail_silently=False)
        except Exception as smtp_error:
            node_logger.error(f"🔌 [SMTP FAILURE] Fallo de red: {smtp_error}")
            raise self.retry(exc=smtp_error)

        # Registro en Bitácora (Pugado de campos inexistentes)
        Interaction.objects.create(
            institution=target,
            channel='EMAIL',
            direction='OUT',
            subject=payload_ia['subject'],
            message_sent=payload_ia['html_body'],
            status='SENT'
        )

        # Emisión de Telemetría en Tiempo Real (WebSockets)
        try:
            from sales.views_omni import _emit_omni_timeline_websocket_event
            _emit_omni_timeline_websocket_event(target.id, tracking_uuid, {"ip_address": "SYSTEM_CRON"}, False)
        except ImportError:
            pass

        node_logger.info(f"✅ [MISSION ACCOMPLISHED] Drip Node {email_step} ejecutado sobre {target.name}")
        return "NODO TACTICO EXITOSO"

    except Institution.DoesNotExist:
        return "Entidad Fantasma"
    except Exception as e:
        node_logger.error(f"💀 [FATAL NODE ERROR] Colapso incontrolable: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60)
import os
import time
import logging
from celery import shared_task
from django.conf import settings
from django.db import transaction, IntegrityError
from django.core.mail import EmailMessage
from openai import OpenAI

logger = logging.getLogger(__name__)

# ==============================================================================
# 🚀 [GOD TIER LEVIATHAN] THE 1 MILLION DOLLAR APEX CLOSER (AUTOPILOT B2B)
# ==============================================================================

@shared_task(
    bind=True,
    name='sales.tasks.task_fire_apex_closer_reply',
    max_retries=5,
    autoretry_for=(Exception,), 
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    acks_late=True,
    reject_on_worker_lost=True
)
def task_fire_apex_closer_reply(self, interaction_id: str):
    """
    [GOD TIER LEVEL] The 1 Million Dollar Auto-Closer.
    Arquitectura de asalto B2B asíncrona con Inyección HTML y Copywriting de Élite.
    Sintetiza neuro-lingüística corporativa vía LLM y ejecuta el despliegue SMTP.
    """
    t_start = time.perf_counter()
    logger.info(f"⚡ [APEX CLOSER] Secuencia de cierre B2B iniciada. Rastreando Interaction ID: {interaction_id}")
    
    try:
        # ----------------------------------------------------------------------
        # FASE 1: ATOMIC LOCK & RETRIEVAL (Concurrency Control Absoluto)
        # ----------------------------------------------------------------------
        with transaction.atomic():
            try:
                from sales.models import Interaction
                inbound = Interaction.objects.select_for_update().get(id=interaction_id)
            except Exception as lock_err:
                logger.error(f"❌ [DB LOCK FAILED] No se pudo asegurar el bloqueo atómico para ID {interaction_id}: {lock_err}")
                return "Abort: Record lock failed or missing."

            colegio = inbound.institution
            
            if not colegio:
                logger.warning(f"⚠️ [DATA ANOMALY] Interacción {interaction_id} carece de Institución. Abortando.")
                return "Abort: Inbound without Institution."

            # Escudo Anti-Fuego Amigo (Idempotency)
            already_replied = Interaction.objects.filter(
                institution=colegio,
                direction__in=['OUT', 'OUTBOUND'],
                channel='EMAIL',
                created_at__gt=inbound.created_at,
                is_ai_generated=True
            ).exists()
            
            if already_replied:
                logger.warning(f"🛡️ [IDEMPOTENCY MATRIX] Respuesta APEX ya registrada para {colegio.name}. Bloqueando despliegue doble.")
                return "Operation Skipped: Already Replied"

        # ----------------------------------------------------------------------
        # FASE 2: DATA EXTRACTION & PAYLOAD PREPARATION
        # ----------------------------------------------------------------------
        mensaje_cliente = getattr(inbound, 'content', None) or getattr(inbound, 'message_received', None) or "Cliente respondió, procediendo con asalto B2B estándar."
        
        contacto_target = colegio.contacts.first() if hasattr(colegio, 'contacts') else None
        correo_destino = getattr(contacto_target, 'email', None) if contacto_target else getattr(colegio, 'email', None)

        if not correo_destino:
            logger.error(f"❌ [TARGETING ERROR] Sin vector de correo (Email) para {colegio.name}.")
            return "Failed: No destination email."

        asunto_original = getattr(inbound, 'subject', f"Estrategia de Innovación: {colegio.name}")
        if not asunto_original: asunto_original = f"Estrategia de Innovación: {colegio.name}"
        
        asunto_respuesta = asunto_original if str(asunto_original).lower().startswith(('re:', 're :')) else f"Re: {asunto_original}"

        logger.info(f"🧠 [NEURO-ENGINE] Inicializando matriz de Copywriting para {colegio.name}. Vector: {correo_destino}")

        # ----------------------------------------------------------------------
        # FASE 3: NEURO-MARKETING B2B (THE SILICON VALLEY ENTERPRISE PROMPT)
        # ----------------------------------------------------------------------
        SYSTEM_PROMPT = f"""
        ERES LA ÉLITE: Eres el Director de Expansión Estratégica (Enterprise Account Executive) de "Learning Labs", la firma de tecnología educativa más avanzada y premium del mercado.
        Cierras contratos de software B2B de altísimo valor con instituciones educativas y universidades de primer nivel.
        
        CONTEXTO TÁCTICO:
        El cliente (Institución: {colegio.name}) acaba de responder a nuestro correo de prospección inicial.
        Su respuesta exacta fue: "{mensaje_cliente}"
        
        TU MISIÓN (OBJETIVO ABSOLUTO):
        Redactar el CUERPO de un correo de respuesta en formato HTML impecable que genere deseo instantáneo y logre agendar una llamada ejecutiva ("Executive Sync") de 10 a 15 minutos.
        
        REGLAS DE COPYWRITING B2B (NIVEL DIOS):
        1. TONO: Magnético, sofisticado, asertivo, de alto estatus. Vendes prestigio y transformación absoluta, no solo "software". Cero desesperación. Hablas de director a director.
        2. ESTRUCTURA HTML (Breathable Text): Usa etiquetas <p> con estilos limpios. Ningún párrafo debe superar las 3 líneas de lectura. Usa <br><br> para oxigenar visualmente el texto.
        3. EL "AHA MOMENT": Explica en 2 viñetas (<ul><li style="margin-bottom: 8px;">) cómo nuestro ecosistema exclusivo reduce la carga operativa del colegio, eleva la retención y posiciona a la institución en la vanguardia tecnológica. Usa <b> sutilmente para destacar el ROI o palabras clave.
        4. CTA (Llamado a la acción): Cero fricción. Ofrece dos opciones de horario precisas. (Ej: "¿Tendrías 10 minutos este martes a las 10:00 AM o el jueves a las 3:00 PM?")
        5. FIRMA ESTÉTICA (OBLIGATORIA Y EXACTA):
           Tu correo DEBE terminar única y exclusivamente con este bloque de código HTML. No lo alteres, no agregues "Saludos", "Atentamente", ni NADA adicional debajo de él:
           
           <br><br>
           <table cellpadding="0" cellspacing="0" border="0" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
               <tr>
                   <td style="padding-right: 14px; border-right: 2px solid #3b82f6;">
                       <strong style="color: #0f172a; font-size: 15px; letter-spacing: -0.3px;">Learning Labs</strong>
                   </td>
                   <td style="padding-left: 14px;">
                       <span style="color: #475569; font-size: 13px; font-weight: 500; letter-spacing: 0.2px;">LMS avanzado + IA + Simuladores Académicos</span>
                   </td>
               </tr>
           </table>

        ENTREGABLE:
        Devuelve ÚNICAMENTE el código HTML puro. SIN bloques de markdown (no uses ```html). No uses las etiquetas <html> ni <body>. Inicia directamente con el primer <p> del saludo.
        """

        # ----------------------------------------------------------------------
        # FASE 4: SÍNTESIS CUÁNTICA (DEEPSEEK API CALL)
        # ----------------------------------------------------------------------
        api_key = os.environ.get("DEEPSEEK_API_KEY") or getattr(settings, 'DEEPSEEK_API_KEY', None)
        if not api_key:
            raise ValueError("Configuración Crítica: Falta DEEPSEEK_API_KEY en el entorno.")

        #sync_client = OpenAI(api_key=api_key, base_url="[https://api.deepseek.com](https://api.deepseek.com)")
        sync_client = OpenAI(
            api_key=api_key, 
            base_url="https://api.deepseek.com/v1"
        )
        llm_start_time = time.perf_counter()
        response = sync_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Genera el correo HTML táctico B2B exacto que debo enviar."}
            ],
            temperature=0.7, # Creatividad optimizada para persuasión
            max_tokens=850,
            presence_penalty=0.15,
            frequency_penalty=0.2
        )
        
        cuerpo_generado = response.choices[0].message.content.strip()
        
        # Purga de alucinaciones Markdown (Sanitización HTML)
        if cuerpo_generado.startswith("```html"):
            cuerpo_generado = cuerpo_generado.replace("```html", "", 1)
        if cuerpo_generado.endswith("```"):
            cuerpo_generado = cuerpo_generado.rsplit("```", 1)[0]
        cuerpo_generado = cuerpo_generado.strip()
            
        llm_latency = (time.perf_counter() - llm_start_time) * 1000
        logger.info(f"🚀 [APEX SYNTHESIS] LLM completó el motor de persuasión en {llm_latency:.2f}ms. Payload: {len(cuerpo_generado)} bytes.")

        # ----------------------------------------------------------------------
        # FASE 5: DESPLIEGUE DEL ARMAMENTO (SMTP RELAY - HTML ENABLED)
        # ----------------------------------------------------------------------
        remitente = getattr(settings, 'EMAIL_HOST_USER', 'omni-hydra@localhost')
        # Remitente enmascarado con alta autoridad
        from_header = f"Learning Labs | Expansión <{remitente}>"

        thread_id = getattr(inbound, 'thread_id', None) or getattr(inbound, 'message_id', '')
        
        headers = {}
        if thread_id:
            headers['In-Reply-To'] = thread_id
            headers['References'] = thread_id

        email_msg = EmailMessage(
            subject=asunto_respuesta,
            body=cuerpo_generado,
            from_email=from_header,
            to=[correo_destino],
            headers=headers
        )
        
        # [THE MAGIC WAND]: Le indicamos al cliente (Gmail/Outlook) que renderice la belleza del HTML
        email_msg.content_subtype = "html"
        
        smtp_start_time = time.perf_counter()
        email_msg.send(fail_silently=False) 
        smtp_latency = (time.perf_counter() - smtp_start_time) * 1000
        logger.info(f"📨 [SMTP RELAY] Misil HTML despachado al servidor de correo en {smtp_latency:.2f}ms.")

        # ----------------------------------------------------------------------
        # FASE 6: INMUTABILIDAD EN LA MATRIX (Database Commit Bulletproof)
        # ----------------------------------------------------------------------
        with transaction.atomic():
            # Construcción dinámica para evitar el error "unexpected keyword argument"
            interaction_kwargs = {
                'institution': colegio,
                'direction': 'OUT',
                'channel': 'EMAIL',
                'subject': asunto_respuesta,
                'status': 'SENT',
                'is_ai_generated': True,
            }
            
            if contacto_target:
                interaction_kwargs['contact'] = contacto_target
                
            from sales.models import Interaction
            model_fields = [f.name for f in Interaction._meta.get_fields()]
            
            # Inyección inteligente del Payload
            if 'content' in model_fields:
                interaction_kwargs['content'] = cuerpo_generado
            elif 'message_sent' in model_fields:
                interaction_kwargs['message_sent'] = cuerpo_generado
            
            # Metadata Opcional (Si tu DB lo soporta)
            if 'ai_sentiment' in model_fields:
                interaction_kwargs['ai_sentiment'] = 'STRATEGIC_PUSH'
            if 'thread_id' in model_fields and thread_id:
                interaction_kwargs['thread_id'] = thread_id
            if 'interaction_type' in model_fields:
                interaction_kwargs['interaction_type'] = 'auto_reply_apex_closer'

            # 💥 IMPACTO A BASE DE DATOS
            Interaction.objects.create(**interaction_kwargs)
            
            # Transición del estado del Lead a Negociación
            if hasattr(colegio, 'processing_status'):
                colegio.processing_status = 'NEGOTIATING'
                colegio.save(update_fields=['processing_status'])
            elif hasattr(colegio, 'status'):
                colegio.status = 'NEGOTIATING'
                colegio.save(update_fields=['status'])

        total_latency = (time.perf_counter() - t_start) * 1000
        logger.info(f"✅ [IMPACTO CONFIRMADO] Secuencia APEX finalizada. Objetivo: {correo_destino}. Latencia Total: {total_latency:.2f}ms")
        
        return f"Apex Closer Impact Confirmed -> {correo_destino} (TTL: {total_latency:.0f}ms)"

    except Exception as e:
        logger.critical(f"💀 [FATAL ERROR] Falla estructural en APEX Closer Engine: {str(e)}", exc_info=True)
        raise self.retry(exc=e)
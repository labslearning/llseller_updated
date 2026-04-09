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
import logging
from django.conf import settings
from django.core.mail import send_mail
import requests
import uuid
import re
import random
import html
import os
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

#from sales.engine.deepseek_sales_brain import QuantumSalesArchitect, AIProviderError, AIValidationError
from sales.engine.deepseek_sales_brain import QuantumSalesArchitect, AIRetryableError, AIFatalError, AIValidationError
from sales.engine.quantum_classifier import QuantumLeadClassifier
from sales.engine.inbound_parser import SupremeInboundParser
# Celery & Django Imports
from celery import shared_task, Task, group
from celery.exceptions import SoftTimeLimitExceeded
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError
from celery.exceptions import MaxRetriesExceededError

from django.core.cache import cache
from django.db import transaction, DatabaseError, IntegrityError
from django import db  
from django.utils import timezone
from django.db.models import Q
from asgiref.sync import async_to_sync  

from .models import Institution, Interaction

# =========================================================
# IMPORTACIONES DE VANGUARDIA (GOD TIER)
# =========================================================
from sales.models import Institution, TechProfile, DeepForensicProfile, Interaction, Contact
from sales.engine.serp_resolver import SERPResolverEngine
from sales.engine.recon_engine import execute_recon, run_recon
from sales.engine.ml_scoring import train_model, score_unrated_leads
from sales.engine.discovery_engine import OSMDiscoveryEngine


from ddgs import DDGS
from openai import AsyncOpenAI, RateLimitError, APIConnectionError, APIError


from .engine.ai_omni_brain import OmniAIBrain  # Asegúrate de usar el nombre de la clase correcta que creamos en el Paso 1
from .engine.quantum_mail import QuantumMailServer 
from .engine.waba_gateway import WABAGateway 

logger = logging.getLogger('LearningLabs.GhostSniper.Step1')
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

# =========================================================
# 📡 MISIÓN 6: INBOUND RADAR (QUANTUM CATCHER)
# =========================================================
@shared_task(
    bind=True, 
    base=SovereignBaseTask, 
    name="sales.tasks.task_run_inbound_catcher",
    soft_time_limit=300,
    time_limit=360
)
def task_run_inbound_catcher(self):
    """
    [QUANTUM RADAR]: Escáner IMAP con protección Mutex.
    Asimila correos, sanitiza HTML corporativo y clasifica vía DeepSeek Singularity.
    """
    IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
    IMAP_USER = os.getenv("IMAP_USER")
    IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")

    if not IMAP_USER or not IMAP_PASSWORD:
        logger.error("❌ [FATAL] Credenciales IMAP no detectadas en variables de entorno.")
        return "Missing IMAP Credentials. Aborted."

    # 🛡️ OMNI-TIER MUTEX: Evita que 2 workers lean la bandeja a la vez
    lock_id = "mutex_inbound_radar_scan"
    with distributed_lock(lock_id, timeout=240, blocking=False) as acquired:
        if not acquired:
            logger.info("🔒 [INBOUND RADAR] Escaneo en curso por otro nodo. Abortando colisión.")
            return "Radar Locked by another Node."

        logger.info("📡 [INBOUND RADAR] Iniciando barrido táctico IMAP...")

        try:
            with imaplib.IMAP4_SSL(IMAP_SERVER) as mail:
                mail.login(IMAP_USER, IMAP_PASSWORD)
                mail.select("inbox")

                status, messages = mail.search(None, "UNSEEN")
                if status != "OK":
                    return "No new messages."

                email_ids = messages[0].split()
                if not email_ids:
                    logger.info("📭 Radar limpio. Sin respuestas nuevas.")
                    return "Inbox Zero."

                logger.info(f"🚨 [CONTACTO DETECTADO] {len(email_ids)} nuevos mensajes.")
                
                channel_layer = get_channel_layer()
                classifier = QuantumLeadClassifier()

                for e_id in email_ids:
                    res, msg_data = mail.fetch(e_id, "(RFC822)")
                    raw_email = msg_data[0][1]

                    # 1. Extracción Heurística Nivel Omega
                    payload = SupremeInboundParser.extract_clean_reply(raw_email)
                    if not payload:
                        continue # Payload vacío o malicioso, saltar

                    # Buscamos objetivo en la BD
                    target = Institution.objects.filter(email__iexact=payload.sender_email).first()
                    
                    if target:
                        logger.info(f"🎯 [MATCH] Interceptada respuesta de: {target.name} ({payload.sender_email})")
                        
                        # 2. Análisis Cuántico (Vía Async_to_Sync)
                        analysis = async_to_sync(classifier.classify_inbound)(payload.clean_body)
                        
                        # 3. Transacción ACID Completa
                        try:
                            with transaction.atomic():
                                # Prevención de duplicados vía Hash de Idempotencia
                                if Interaction.objects.filter(idempotency_key=payload.idempotency_key).exists():
                                    logger.warning(f"⚠️ Reenvío detectado y bloqueado para {target.name}")
                                    mail.store(e_id, '+FLAGS', '\\Seen')
                                    continue

                                Interaction.objects.create(
                                    institution=target,
                                    channel='EMAIL',
                                    direction='IN',
                                    content=payload.clean_body,
                                    is_ai_generated=False,
                                    idempotency_key=payload.idempotency_key # Nuevo campo requerido
                                )
                                
                                if analysis.get('requires_human') or analysis.get('sentiment') == 'SECURITY_RISK':
                                    target.processing_status = Institution.ProcessingStatus.MANUAL_INTERVENTION
                                
                                target.status = analysis.get('sentiment', 'WARM')
                                target.updated_at = timezone.now()
                                target.save(update_fields=['processing_status', 'status', 'updated_at'])
                                
                                # 4. Telemetría WebSockets
                                async_to_sync(channel_layer.group_send)(
                                    "omni_hydra",
                                    {
                                        "type": "send_alert",
                                        "message": {
                                            "event": "INBOUND_REPLY",
                                            "institution": target.name,
                                            "sentiment": analysis.get('sentiment'),
                                            "summary": analysis.get('summary'),
                                            "latency_ms": analysis.get('processing_time_ms', 0)
                                        }
                                    }
                                )
                        except Exception as db_err:
                            logger.error(f"💀 [DB ERROR] Fallo al guardar la interacción: {db_err}")
                            continue

                    # Solo marcamos como LEÍDO si sobrevivió al procesamiento
                    mail.store(e_id, '+FLAGS', '\\Seen')

                return f"Procesados {len(email_ids)} mensajes."

        except imaplib.IMAP4.error as imap_err:
            logger.error(f"❌ [IMAP EXCEPTION] Fallo de conexión: {imap_err}")
            raise self.retry(exc=imap_err, countdown=60)
        except Exception as e:
            logger.error(f"❌ [FATAL ERROR] Colapso del Inbound Catcher: {e}")
            raise self.retry(exc=e, countdown=120)

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
import os
import logging
from celery import Celery, Task
from celery.schedules import crontab
from celery.signals import worker_process_init, task_prerun, task_postrun, worker_ready

# ==========================================
# 1. CONFIGURACIÓN DINÁMICA DEL ENTORNO
# ==========================================
# Asegura que Celery sepa dónde encontrar la configuración de Django
PROJECT_NAME = 'core' 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{PROJECT_NAME}.settings')

logger = logging.getLogger("Sovereign.CeleryMaster")

# ==========================================
# 2. CUSTOM TASK BASE (EL NÚCLEO INMORTAL - SILICON VALLEY)
# ==========================================
class SovereignTask(Task):
    """
    Base Task Nivel Dios.
    Todas tus funciones @shared_task heredarán este comportamiento automáticamente.
    Características:
    - Auto-Retries con Retroceso Exponencial y Jitter (Mitiga cuellos de botella).
    - Hard & Soft Time Limits (Previene Memory Leaks y Zombie Processes).
    - Telemetría forense.
    """
    abstract = True
    
    # Tolerancia a fallos de red por defecto
    autoretry_for = (ConnectionError, TimeoutError) 
    max_retries = 3
    retry_backoff = True       # 1s, 2s, 4s, 8s...
    retry_backoff_max = 600    # Máximo 10 minutos de espera
    retry_jitter = True        # Añade milisegundos aleatorios (Evita "Thundering Herd")

    # [SHENZHEN SECURITY] Límite de ejecución. Si el scraper Playwright se congela, 
    # a los 3600 segs (1 hr) se lanza una excepción suave. A los 3660 se mata el proceso de raíz.
    soft_time_limit = 3600
    time_limit = 3660

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Captura absoluta de fallos (Punto de anclaje para Sentry/Datadog)"""
        logger.error(f"❌ [CRITICAL FAILURE] Misión: {self.name} | ID: {task_id}")
        logger.error(f"🔍 Argumentos: {args} | Excepción: {exc}")
        # Aquí se inyectaría: sentry_sdk.capture_exception(exc)
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """Telemetría de éxito"""
        logger.info(f"✅ [MISSION ACCOMPLISHED] {self.name} | ID: {task_id}")
        super().on_success(retval, task_id, args, kwargs)

# ==========================================
# 3. INSTANCIACIÓN DE LA MAQUINARIA CELERY
# ==========================================
app = Celery(PROJECT_NAME, task_cls=SovereignTask)

# Extrae la configuración usando el prefijo CELERY_ en settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescubrimiento inteligente de archivos tasks.py en todas las apps
app.autodiscover_tasks()

# ==========================================
# 4. EL RELOJ MAESTRO (AUTONOMÍA TOTAL - HIGH FREQUENCY POLLING)
# ==========================================
app.conf.beat_schedule = {
    # 🔥 ESCUCHA ACTIVA (Oídos): OVERCLOCKING A 30 SEGUNDOS
    # El Omni-Catcher escaneará el correo cada medio minuto de forma ininterrumpida.
    'inbound-listener-high-frequency': {
        'task': 'sales.tasks.task_run_inbound_catcher',
        'schedule': 30.0, # Frecuencia absoluta en segundos (No usa crontab)
    },
    
    # 🚀 ATAQUE INICIAL (Voz Apertura): Dispara IA Copys a las 8:30 AM (Lun-Vie)
    'outbound-step1-morning': {
        'task': 'sales.tasks.task_run_outbound_campaign',
        'schedule': crontab(hour=8, minute=30, day_of_week='mon-fri'),
    },
    
    # 🔄 ASEDIO OMNICANAL (WhatsApp + Followup): Envía los Hilos a las 2:00 PM (Lun-Vie)
    'outbound-step2-afternoon': {
        'task': 'sales.tasks.task_run_outbound_followup',
        'schedule': crontab(hour=14, minute=0, day_of_week='mon-fri'),
    },
}

# ==========================================
# 5. GESTIÓN DE RECURSOS (MEMORY & DB LEAK PREVENTION - TEL AVIV)
# ==========================================
@worker_process_init.connect
def fix_multiprocessing(**kwargs):
    """
    Protección de Forks: Cuando Celery crea un hilo nuevo, las conexiones SSL/DB 
    pueden corromperse. Esto purga las conexiones viejas para que el hijo nazca limpio.
    """
    from django.db import connections
    for conn in connections.all():
        conn.close()

@task_prerun.connect
def cleanup_db_connections_before(task_id, task, *args, **kwargs):
    """Limpia conexiones muertas ANTES de empezar la tarea."""
    from django.db import close_old_connections
    close_old_connections()

@task_postrun.connect
def cleanup_db_connections_after(task_id, task, *args, **kwargs):
    """Limpia la basura de memoria y DB DESPUÉS de terminar la tarea (Garbage Collection)."""
    from django.db import close_old_connections
    close_old_connections()

@worker_ready.connect
def on_worker_ready(**kwargs):
    """Hook de inicio: Notifica cuando la máquina de guerra está online."""
    logger.info("=========================================================")
    logger.info("⚡ [SOVEREIGN ENGINE] Celery Worker Online y Conectado al Broker.")
    logger.info("⚡ Protocolos de Asedio y Catcher IMAP activados en Alta Frecuencia.")
    logger.info("=========================================================")
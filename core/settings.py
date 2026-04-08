"""
================================================================================
[TRANSCENDENT GOD TIER ARCHITECTURE: OMEGA QUANTUM LEVIATHAN CLASS V106]
PROJECT: GHOST SNIPER - SOVEREIGN INTELLIGENCE ENGINE (PROJECT OMNISCIENT)
STANDARDS: UNIT 8200 SPEC / SILICON WADI / 12-FACTOR APP / ISO-27001 / SOC2
ENGINEERING: NATIVE DJANGO 5.x REDIS POOLING (FLAT ARCHITECTURE), 
             FAILSAFE NETWORK RESOLUTION, ASGI DEADLOCK PREVENTION, 
             ENTERPRISE LOGGING FORENSICS, ZERO-TRUST COOKIE MESH.
================================================================================
"""

import os
import sys
import socket
from pathlib import Path
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured
from celery.schedules import crontab
from dotenv import load_dotenv
import dj_database_url

# ==============================================================================
# 🏗️ [NIVEL DIOS 1]: CORE TOPOLOGY & ENV CIRCUIT BREAKER
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# [SPEC]: Carga de entorno con protección contra 'Ghost Variables'
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=False)

def get_env_var(var_name, default=None, required=False):
    """Encapsulación de variables con validación estricta y limpieza de tipos."""
    val = os.getenv(var_name, default)
    if required and val is None:
        raise ImproperlyConfigured(f"🚨 CRITICAL INFRASTRUCTURE FAILURE: {var_name} missing.")
    # Sanitización de booleanos puros
    if str(val).lower() in ('true', '1', 'yes'): return True
    if str(val).lower() in ('false', '0', 'no'): return False
    return val

def is_docker():
    """Detección heurística de entorno Docker (Cgroups)"""
    path = '/proc/self/cgroup'
    return os.path.exists('/.dockerenv') or (os.path.isfile(path) and any('docker' in line for line in open(path)))

def resolve_redis_host():
    """Resolución dinámica de host para Redes Híbridas (Failsafe DNS)"""
    if not is_docker():
        return '127.0.0.1' # Ejecución directa en Host OS (ej: Parrot)
    try:
        socket.gethostbyname('redis')
        return 'redis'
    except socket.gaierror:
        return '127.0.0.1'

# ==============================================================================
# 🛡️ [NIVEL DIOS 2]: CYBER-SECURITY & ZERO-TRUST POLICY
# ==============================================================================
SECRET_KEY = get_env_var('DJANGO_SECRET_KEY', required=True)
DEBUG = get_env_var('DJANGO_DEBUG', False)

raw_hosts = get_env_var('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [host.strip() for host in str(raw_hosts).split(',') if host.strip()]

if not DEBUG:
    SECURE_SSL_REDIRECT = get_env_var('DJANGO_SECURE_SSL_REDIRECT', True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    # [NIVEL DIOS FIX]: Prevención de ataques Cross-Site
    SESSION_COOKIE_SAMESITE = 'Strict' 
    CSRF_COOKIE_SAMESITE = 'Strict'
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 63072000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# ==============================================================================
# 📦 [NIVEL DIOS 3]: SYSTEM GEOMETRY & MIDDLEWARE MESH
# ==============================================================================
INSTALLED_APPS = [
    'daphne', # Nucleus ASGI (High-Concurrency Engine - SIEMPRE DEBE IR PRIMERO)
    'unfold', # Tactical Admin Interface
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # [SOVEREIGN MODULES]
    'sales.apps.SalesConfig', 
    'channels', # WebSocket Multiplexing
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Static assets O(1)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# ==============================================================================
# 🗄️ [NIVEL DIOS 4]: PERSISTENCE LAYER (FAILSAFE DATABASE ROUTING)
# ==============================================================================
DATABASES = {
    'default': dj_database_url.config(
        default=get_env_var('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

if 'sqlite' not in DATABASES['default']['ENGINE']:
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
    }
    # [NIVEL DIOS FIX]: Timeout de sentencias en Postgres para evitar Thread-Locks
    if 'postgresql' in DATABASES['default']['ENGINE']:
        DATABASES['default']['OPTIONS']['options'] = '-c statement_timeout=30000'

# ==============================================================================
# 🧠 [NIVEL DIOS 5]: DISTRIBUTED MEMORY (DJANGO 5 NATIVE REDIS POOLING)
# ==============================================================================

# [GOD TIER V108 FIX]: OVERRIDE ABSOLUTO. 
# Ignoramos el .env y forzamos la conexión a localhost para el entorno de desarrollo local en Parrot OS.
REDIS_URL = "redis://127.0.0.1:6379/0"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL.replace('/0', '/1'), # DB 1 aislada para Cache
        "OPTIONS": {
            "max_connections": 1000, 
            "retry_on_timeout": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        }
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL], 
            "capacity": 2000, 
            "expiry": 30, 
            "group_expiry": 86400,
        },
    },
}

# ==============================================================================
# ⚙️ [NIVEL DIOS 6]: CELERY AUTONOMOUS ORCHESTRATOR
# ==============================================================================
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Bogota'
CELERY_ENABLE_UTC = False

CELERY_WORKER_MAX_TASKS_PER_CHILD = 50 
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  
CELERY_TASK_ACKS_LATE = True           
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_SOFT_TIME_LIMIT = 300 
CELERY_TASK_TIME_LIMIT = 360 

CELERY_TASK_ROUTES = {
    'sales.tasks.task_run_ghost_sniper': {'queue': 'scraping_queue'},
    'sales.tasks.task_run_osm_radar': {'queue': 'discovery_queue'},
    'sales.tasks.*': {'queue': 'default'},
}

CELERY_BEAT_SCHEDULE = {
    'poll_inbox_every_5_mins': {
        'task': 'sales.tasks.task_run_inbound_catcher',
        'schedule': 300.0, 
    },
    'daily_intelligence_scoring': {
        'task': 'sales.tasks.task_batch_score_leads',
        'schedule': crontab(hour=1, minute=0),
        'kwargs': {'limit': 2000}
    },
    'weekly_neural_retraining': {
        'task': 'sales.tasks.task_retrain_ai_model',
        'schedule': crontab(hour=3, minute=0, day_of_week='sunday'),
    },
}

# ==============================================================================
# 📧 [NIVEL DIOS 7]: MULTI-VECTOR COMMUNICATIONS (SMTP/IMAP)
# ==============================================================================
SMTP_PASSWORD = get_env_var('EMAIL_HOST_PASSWORD')

if not SMTP_PASSWORD and DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = get_env_var('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(get_env_var('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = get_env_var('EMAIL_HOST_USER', required=True)
EMAIL_HOST_PASSWORD = SMTP_PASSWORD

DEFAULT_FROM_EMAIL = f"Learning Labs <{EMAIL_HOST_USER}>"
SERVER_EMAIL = EMAIL_HOST_USER

IMAP_SERVER = get_env_var("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = 993
IMAP_USERNAME = EMAIL_HOST_USER
IMAP_PASSWORD = EMAIL_HOST_PASSWORD

# ==============================================================================
# 📊 [NIVEL DIOS 8]: ENTERPRISE OBSERVABILITY (LOGGING)
# ==============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'omega': {
            'format': '%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(lineno)d] >> %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'omega',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django.server': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django.request': {'handlers': ['console'], 'level': 'ERROR', 'propagate': False},
        'django.channels.server': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'Sovereign': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'sales': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'urllib3': {'handlers': ['null'], 'level': 'INFO', 'propagate': False},
        'celery': {'handlers': ['console'], 'level': 'INFO', 'propagate': False}, # Control del ruido de Celery
    },
}

# ==============================================================================
# 🤖 [NIVEL DIOS 9]: AI & QUANTUM ANALYTICS
# ==============================================================================
DEEPSEEK_API_KEY = get_env_var("DEEPSEEK_API_KEY", required=True)
CONSCIOUSNESS_LEVEL = get_env_var("CONSCIOUSNESS_LEVEL", "ultimate")

# ==========================================
# 🎨 UI/UX ARCHITECTURE (UNFOLD ELITE)
# ==========================================
LANGUAGE_CODE = 'es-co' 
TIME_ZONE = 'America/Bogota' 
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

UNFOLD = {
    "SITE_TITLE": "Sovereign Intelligence",
    "SITE_HEADER": "Omni-Hydra Command Center",
    "SITE_SYMBOL": "radar",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "#f0fdfa", "100": "#ccfbf1", "200": "#99f6e4", "300": "#5eead4",
            "400": "#2dd4bf", "500": "#14b8a6", "600": "#0d9488", "700": "#0f766e",
            "800": "#115e59", "900": "#134e4a",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "CENTRO DE OPERACIONES",
                "separator": True,
                "items": [
                    {"title": "Radar Institucional", "icon": "domain", "link": "/admin/sales/institution/"},
                    {"title": "Ghost Sniper Console", "icon": "target", "link": "/admin/sales/sniperconsole/"},
                ],
            },
            {
                "title": "INTELIGENCIA OMNICANAL",
                "separator": True,
                "items": [
                    {"title": "Interacciones Live", "icon": "forum", "link": "/admin/sales/interaction/"},
                    {"title": "Métricas de Impacto", "icon": "monitoring", "link": "/admin/sales/commandcenter/"},
                ],
            },
        ],
    },
}
# sales/engine/waba_gateway.py

"""
================================================================================
[GOD TIER OMEGA ARCHITECTURE: WABA CLOUD GATEWAY V1000.0 APEX]
MODULE: DISTRIBUTED META GRAPH API INTEGRATION & FORENSIC NETWORKING
ENGINEERING ACHIEVEMENTS (SILICON WADI / TOKYO / UNIT 8200 STANDARD):
- 🌐 Distributed Circuit Breaker: Cortocircuito apoyado en Redis. Conciencia global del Clúster.
- ⚡ TCP Window Optimization: Timeout asimétrico (3.05s connect / 15s read) alineado al stack TCP/IP del Kernel.
- 🛡️ C10K Thread-Safe Pooling: urllib3 HTTPAdapter con reutilización de Sockets TLS.
- 🧠 Graph API Deep Parser: Análisis semántico de sub-códigos de error de Meta (Evita falsos positivos).
- 🔐 L7 Idempotency Lock: Bloqueo de ráfagas accidentales (Previene doble cobro de Meta por reconexiones).
- 🧹 MSISDN Forensic Heuristics: Destrucción de extensiones corporativas y prefijos espurios.
================================================================================
"""

import os
import re
import time
import uuid
import logging
import threading
import random
import hashlib
from typing import Optional, Dict, Any, Final

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from django.conf import settings
from django.core.cache import cache

# Logger forense de operaciones de red
logger = logging.getLogger("Sovereign.WABAGateway")

# =====================================================================
# 🌐 DISTRIBUTED CIRCUIT BREAKER (Clúster-Aware Layer 7 Defense)
# =====================================================================
class DistributedMetaCircuitBreaker:
    """
    Cortocircuito Distribuido. Utiliza Redis (vía Django Cache) para compartir 
    el estado de salud de la API de Meta entre múltiples workers y servidores.
    Previene el colapso masivo (Cascading Failures) en toda la flota.
    """
    __slots__ = ('failure_threshold', 'recovery_timeout', 'cache_key_failures', 'cache_key_state', 'cache_key_time')

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.cache_key_failures = "waba_cb_failures"
        self.cache_key_state = "waba_cb_state"
        self.cache_key_time = "waba_cb_last_failure"

    def can_execute(self) -> bool:
        state = cache.get(self.cache_key_state, "CLOSED")
        
        if state == "CLOSED":
            return True
            
        if state == "OPEN":
            last_failure = cache.get(self.cache_key_time, 0.0)
            if time.time() - last_failure >= self.recovery_timeout:
                # Transición segura a HALF_OPEN para toda la flota
                cache.set(self.cache_key_state, "HALF_OPEN", timeout=self.recovery_timeout)
                logger.warning("🔄 [Distributed WABA Breaker] Estado HALF_OPEN. Iniciando tráfico de sondeo (Surgical Probing).")
                return True
            return False
            
        if state == "HALF_OPEN":
            # Sondeo Estocástico: Dejar pasar solo el 15% del tráfico global
            return random.random() < 0.15

        return False

    def record_success(self):
        state = cache.get(self.cache_key_state, "CLOSED")
        if state != "CLOSED":
            logger.info("✅ [Distributed WABA Breaker] Nodos de Meta estabilizados. Circuito CERRADO globalmente.")
            cache.set(self.cache_key_state, "CLOSED", timeout=None)
            cache.delete(self.cache_key_failures)

    def record_failure(self):
        # Incremento atómico en Redis
        try:
            failures = cache.incr(self.cache_key_failures)
        except ValueError:
            # Si la llave no existe, inicializarla
            cache.set(self.cache_key_failures, 1, timeout=self.recovery_timeout * 2)
            failures = 1
            
        cache.set(self.cache_key_time, time.time(), timeout=self.recovery_timeout * 2)
        
        state = cache.get(self.cache_key_state, "CLOSED")
        if failures >= self.failure_threshold and state != "OPEN":
            cache.set(self.cache_key_state, "OPEN", timeout=self.recovery_timeout)
            logger.critical(f"🚨 [Distributed WABA Breaker] ROTURA DETECTADA (Fallos: {failures}). Bloqueando flota saliente hacia Meta API.")

# Instancia Global
distributed_waba_breaker = DistributedMetaCircuitBreaker()


# =====================================================================
# 🛡️ NORMALIZACIÓN FORENSE (E.164 Strict)
# =====================================================================
class ForensicMSISDNNormalizer:
    @staticmethod
    def sanitize(raw_phone: str) -> str:
        """
        [E.164 HEURISTIC PURGE]
        Destruye basura OSINT, extensiones corporativas (ext, x) y formatea a estándar internacional.
        """
        if not raw_phone:
            return ""
        
        phone_str = str(raw_phone).strip().lower()
        
        # 1. Destrucción de extensiones (Ej: "+57 300 1234 ext 55" -> "+57 300 1234")
        phone_str = re.split(r'ext|x|p', phone_str)[0]
        
        # 2. Purga de prefijos de salida internacional antiguos ('00')
        if phone_str.startswith('00'):
            phone_str = phone_str[2:]
            
        # 3. Aniquilación de caracteres no numéricos
        sanitized = re.sub(r'\D', '', phone_str)
        
        return sanitized


# =====================================================================
# ⚙️ MOTOR DE COMUNICACIÓN CLOUD (WABA GATEWAY)
# =====================================================================
class WABAGateway:
    """
    [APEX TIER WHATSAPP ENGINE]
    Pasarela distribuida hiper-optimizada.
    """
    
    MAX_MESSAGE_LENGTH: Final[int] = 4096
    API_VERSION: Final[str] = "v19.0"
    
    # Thread-Local Storage para Pools TCP (Evita colisiones entre hilos del mismo Worker)
    _thread_local = threading.local()

    @classmethod
    def _get_thread_safe_session(cls) -> requests.Session:
        """
        [THREAD-SAFE TCP POOLING & L4 RESILIENCE]
        """
        if not hasattr(cls._thread_local, "session"):
            session = requests.Session()
            
            # L4 Retry Backoff: Cubre micro-cortes TCP sin alarmar al L7 Circuit Breaker
            retry_strategy = Retry(
                total=3,
                backoff_factor=0.5, # 0.5, 1.0, 2.0s
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["POST"],
                respect_retry_after_header=True
            )
            
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=20, 
                pool_maxsize=20
            )
            
            session.mount("https://", adapter)
            cls._thread_local.session = session
            logger.debug(f"🔌 [WABAGateway] Session Pool TCP/TLS anclado al Hilo {threading.get_ident()}.")
            
        return cls._thread_local.session

    @staticmethod
    def _mask_token(token: str) -> str:
        """[FORENSIC SANITIZATION] Oculta Bearer Tokens en volcados de memoria/logs."""
        if not token or len(token) < 15:
            return "***[INVALID_TOKEN]***"
        return f"{token[:5]}...[REDACTED]...{token[-5:]}"

    @classmethod
    def _parse_meta_error(cls, response: requests.Response) -> bool:
        """
        [DEEP GRAPH API PARSER]
        Decodifica el JSON de error de Meta. Si es error del usuario (Ej. Número inválido),
        retorna False (No disparar Circuit Breaker). Si es error de Meta (Caída), retorna True.
        """
        try:
            error_data = response.json().get('error', {})
            code = error_data.get('code', 0)
            subcode = error_data.get('error_subcode', 0)
            
            # Códigos de error atribuibles al Cliente/Lead (No es caída de API)
            # 131009: Parameter value is not valid
            # 131030: Recipient phone number not in allowed list
            # 131026: Message undeliverable
            if code in [100, 190] or subcode in [131009, 131030, 131026, 133010]:
                logger.error(f"⚠️ [Graph API] Rechazo Semántico de Meta (Código {code}/{subcode}): {error_data.get('message')}")
                return False # No es caída de sistema
                
            return True # Fallo estructural o de infraestructura de Meta
        except Exception:
            return True # Ante la duda de un payload corrupto, asumimos fallo de Meta

    @classmethod
    def send_message(cls, phone: str, message: str) -> bool:
        """
        [DISPARO TÁCTICO WABA]
        Transmite la ojiva lingüística hacia el dispositivo celular del prospecto.
        """
        trace_id = f"WABA-{uuid.uuid4().hex[:8].upper()}"
        
        # 1. EVALUACIÓN DE CORTOCIRCUITO DISTRIBUIDO
        if not distributed_waba_breaker.can_execute():
            logger.warning(f"[{trace_id}] 🚫 Disparo abortado. Nodos Meta Graph aislados por Circuit Breaker Global.")
            return False

        # 2. VALIDACIÓN DE ENTORNO
        access_token = getattr(settings, 'WABA_ACCESS_TOKEN', os.environ.get('WABA_ACCESS_TOKEN'))
        phone_number_id = getattr(settings, 'WABA_PHONE_NUMBER_ID', os.environ.get('WABA_PHONE_NUMBER_ID'))
        
        if not access_token or not phone_number_id:
            logger.critical(f"[{trace_id}] 🛑 PÁNICO DE SISTEMA: Credenciales WABA no inyectadas en el entorno.")
            return False

        # 3. NORMALIZACIÓN FORENSE E.164
        clean_phone = ForensicMSISDNNormalizer.sanitize(phone)
        if len(clean_phone) < 10 or len(clean_phone) > 15:
            logger.error(f"[{trace_id}] 🛑 Aborto: MSISDN anómalo o fuera de norma internacional ({clean_phone}).")
            return False

        # 4. IDEMPOTENCY ANTI-SPAM LOCK (Capa 7)
        # Garantiza que Celery no mande el mismo mensaje si el Worker se reinicia repentinamente.
        payload_signature = hashlib.md5(f"{clean_phone}:{message[:100]}".encode()).hexdigest()
        idempotency_key = f"waba_lock_{payload_signature}"
        
        if not cache.add(idempotency_key, "LOCKED", 30): # Bloqueo de 30 segundos
            logger.warning(f"[{trace_id}] 🛡️ Supresión de Fuego Amigo: Mensaje idéntico detectado en tránsito para {clean_phone}.")
            return False

        # 5. ENSAMBLAJE DE OJIVA Y TRUNCAMIENTO
        safe_message = message if len(message) <= cls.MAX_MESSAGE_LENGTH else message[:cls.MAX_MESSAGE_LENGTH - 3] + "..."
        endpoint = f"https://graph.facebook.com/{cls.API_VERSION}/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {
                "preview_url": True, # Inyección visual de Link Preview
                "body": safe_message
            }
        }

        # 6. SECUENCIA DE TRANSMISIÓN TCP/TLS
        logger.info(f"[{trace_id}] 🚀 Inyectando ojiva a Meta Graph. Blanco: {clean_phone}...")
        
        try:
            start_time = time.perf_counter()
            session = cls._get_thread_safe_session()
            
            # TCP Optimization: 3.05s connect evita timeouts por retransmisión SYN, 15s read protege al worker.
            response = session.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=(3.05, 15.0) 
            )
            
            latency = (time.perf_counter() - start_time) * 1000
            
            if response.status_code in (200, 201):
                distributed_waba_breaker.record_success()
                
                meta_data = response.json()
                msg_id = meta_data.get('messages', [{}])[0].get('id', 'UNKNOWN_META_ID')
                logger.info(f"[{trace_id}] ✅ IMPACTO WABA CONFIRMADO. MetaID: {msg_id}. Latencia: {latency:.2f}ms.")
                return True
            else:
                logger.error(f"[{trace_id}] ❌ META DENEGADO (HTTP {response.status_code}): {response.text}")
                
                # Análisis Profundo: ¿Es culpa de Meta o del Cliente?
                is_systemic_failure = cls._parse_meta_error(response)
                if is_systemic_failure and response.status_code >= 500:
                    distributed_waba_breaker.record_failure()
                    
                return False
                
        except requests.exceptions.Timeout:
            distributed_waba_breaker.record_failure()
            logger.error(f"[{trace_id}] ⏱️ TIMEOUT: Nodos de Meta mudos tras 15s. Latencia crítica.")
            return False
            
        except requests.exceptions.RequestException as e:
            distributed_waba_breaker.record_failure()
            masked_error = str(e).replace(access_token, cls._mask_token(access_token))
            logger.critical(f"[{trace_id}] 💀 Falla de Transporte (L4/L7): {masked_error}")
            return False
            
        except Exception as kernel_panic:
            logger.critical(f"[{trace_id}] 💀 Pánico en Gateway: {kernel_panic}", exc_info=True)
            return False
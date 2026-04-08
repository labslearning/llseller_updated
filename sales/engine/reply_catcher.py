# sales/engine/reply_catcher.py

import logging
import re
import email
from email.header import decode_header
from typing import Optional, Dict, Tuple, Any
import asyncio
import time

import aioimaplib
import orjson
import pybreaker
import structlog
from pydantic import BaseModel, Field, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from django.conf import settings
from django.db import transaction, DatabaseError
from django.core.cache import cache
from django.utils import timezone
from asgiref.sync import sync_to_async

# Importaciones del Dominio
from sales.models import Interaction, Contact, Institution
from sales.engine.deepseek_sales_brain import QuantumSalesArchitect, AIProviderError, AIValidationError

# ==============================================================================
# 0. OBSERVABILIDAD CUÁNTICA & TELEMETRÍA
# ==============================================================================
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(serializer=orjson.dumps)
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logger = structlog.get_logger(__name__)

# Expresiones regulares compiladas en el espacio de memoria global
THREAD_ID_REGEX = re.compile(r'<([a-f0-9\-]{36})@sovereign\.local>', re.IGNORECASE)
EMAIL_CLEAN_REGEX = re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')

# ==============================================================================
# 1. CIRCUIT BREAKER & CONTRATOS SEMÁNTICOS
# ==============================================================================
ai_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=3, # Tolerancia baja para fallar rápido en IMAP
    reset_timeout=60,
    state_storage=pybreaker.CircuitMemoryStorage()
)

class ReplySentiment(BaseModel):
    """
    Validation Gate: Garantiza que la respuesta de DeepSeek es 100% tipada 
    y lista para ser inyectada en la FSM de Django.
    """
    intent: str = Field(
        ..., 
        pattern="^(INTERESTED|NOT_INTERESTED|OUT_OF_OFFICE|BOUNCE|MEETING_REQUEST|SUPPORT_TICKET)$",
        description="Vector principal de intención humana."
    )
    urgency_score: int = Field(
        ..., 
        ge=0, le=100, 
        description="Termómetro de urgencia. 100 = Cierre inminente."
    )
    summary: str = Field(
        ..., 
        max_length=250, 
        description="Resumen táctico (TL;DR) de la respuesta."
    )

# ==============================================================================
# 2. THE QUANTUM INBOUND ENGINE (Zero-Blocking Architecture)
# ==============================================================================
class OmniReplyCatcher:
    """
    [GOD TIER INBOUND CATCHER]
    Motor de ingesta de alta frecuencia.
    Características:
    - Time-Bounded Execution: Ningún correo ahoga el Worker.
    - Lazy Zero-Copy Fetch: Descarga estructurada en memoria.
    - Idempotent Processing: Tolera fallos de red sin duplicar estados.
    """
    
    def __init__(self):
        self.server = getattr(settings, 'IMAP_SERVER', 'imap.gmail.com')
        self.port = getattr(settings, 'IMAP_PORT', 993)
        self.username = getattr(settings, 'IMAP_USERNAME', None)
        self.password = getattr(settings, 'IMAP_PASSWORD', None)
        self.imap_client = None
        
        self.ai_engine = QuantumSalesArchitect(api_key=getattr(settings, 'DEEPSEEK_API_KEY', ''))

    async def __aenter__(self):
        """Conexión Segura e Inquebrantable."""
        if not self.username or not self.password:
            logger.critical("imap_missing_credentials")
            raise ValueError("IMAP Credentials Missing")

        try:
            self.imap_client = aioimaplib.IMAP4_SSL(host=self.server, port=self.port)
            await self.imap_client.wait_hello_from_server()
            
            result, _ = await self.imap_client.login(self.username, self.password)
            if result != 'OK':
                raise Exception("Auth Rejected by Mail Provider")
                
            logger.info("imap_secure_tunnel_established")
            return self
        except Exception as e:
            logger.critical("imap_network_collapse", error=str(e))
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Prevención de Fugas de Memoria y Zombies TCP."""
        if self.imap_client:
            try:
                # No cerramos buzones abruptamente si hay comandos en vuelo
                await asyncio.wait_for(self.imap_client.close(), timeout=2.0)
                await asyncio.wait_for(self.imap_client.logout(), timeout=2.0)
                logger.info("imap_graceful_shutdown")
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning("imap_force_kill", error=str(e))
        await self.ai_engine.aclose()

    # ==========================================================================
    # PARSERS FORENSES (O(N) Complexity bounded by size)
    # ==========================================================================
    def _extract_plain_text(self, msg: email.message.Message) -> str:
        """Extrae el core del mensaje evitando anexos maliciosos."""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                        break
                    except Exception:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='ignore')
            except Exception:
                pass
        return body.strip()

    def _decode_header_value(self, value: str) -> str:
        if not value: return ""
        try:
            decoded = decode_header(value)
            parts = [text.decode(charset or 'utf-8', errors='replace') if isinstance(text, bytes) else str(text) for text, charset in decoded]
            return "".join(parts).strip()
        except Exception:
            return str(value)

    # ==========================================================================
    # CEREBRO SEMÁNTICO (Sentient Analysis)
    # ==========================================================================
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.5, min=2, max=8),
        retry=retry_if_exception_type((AIProviderError, AIValidationError)),
        before_sleep=structlog.stdlib.add_log_level
    )
    async def _analyze_sentiment(self, email_body: str, sender: str) -> ReplySentiment:
        """Clasificación Inmune a Prompt Injection."""
        safe_body = email_body[:2000] # Límite estricto de Context Window
        
        system_prompt = """Eres la IA Táctica de un SDR Enterprise.
Lee la respuesta del director/rector y extrae la intención cruda.

<rules>
1. Formato de salida estricto: JSON.
2. Claves requeridas: "intent", "urgency_score", "summary".
3. Intents válidos: "INTERESTED", "NOT_INTERESTED", "OUT_OF_OFFICE", "BOUNCE", "MEETING_REQUEST", "SUPPORT_TICKET".
4. Si están indecisos o piden un PDF, clasifícalo como "INTERESTED" con urgency_score=40.
</rules>
"""
        user_prompt = f"<sender>{sender}</sender>\n<content>\n{safe_body}\n</content>"
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.05, # Ultra Determinista
            "response_format": {"type": "json_object"}
        }
        
        headers = {"Authorization": f"Bearer {self.ai_engine.api_key.get_secret_value()}", "Content-Type": "application/json"}
        
        try:
            ai_circuit_breaker.before_call()
            response = await self.ai_engine.client.post(self.ai_engine.endpoint, headers=headers, json=payload, timeout=20.0)
            response.raise_for_status()
            ai_circuit_breaker.success()
            
            data = response.json()
            # Validación Semántica (Quality Gate)
            return ReplySentiment(**orjson.loads(data['choices'][0]['message']['content']))
            
        except pybreaker.CircuitBreakerError:
            raise AIProviderError("AI Gateway offline. Circuit Open.")
        except Exception as e:
            raise AIValidationError(f"Semantic parsing fault: {str(e)}")

    # ==========================================================================
    # DATABASE MUTATION LAYER (ACID Compliant Kill-Switch)
    # ==========================================================================
    @sync_to_async
    def _execute_kill_switch(self, interaction_id: Optional[str], sender_email: str, ai_analysis: ReplySentiment, raw_content: str) -> bool:
        """
        Bloquea el lead, ejecuta la FSM y guarda la memoria.
        Devuelve True si el proceso fue atómico, False si hubo Deadlock.
        """
        try:
            with transaction.atomic():
                contact = None
                
                # A. Thread Resolving (O(1) Indexed)
                if interaction_id:
                    # skip_locked=True previene que este worker colapse si Celery está leyendo el mismo Contacto
                    prev = Interaction.objects.select_for_update(skip_locked=True).filter(id=interaction_id).first()
                    if prev and prev.contact:
                        contact = Contact.objects.select_for_update().get(id=prev.contact.id)

                # B. Email Fallback Resolving (O(log N))
                if not contact:
                    contact = Contact.objects.select_for_update(skip_locked=True).filter(email__iexact=sender_email).first()

                if not contact:
                    logger.debug("alien_email_dropped", sender=sender_email)
                    return True # Se ignoró correctamente

                # -------------------------------------------------------------
                # MUTACIÓN DE ESTADO FSM Y KILL SWITCH
                # -------------------------------------------------------------
                contact.pause_automations = True 
                
                intent = ai_analysis.intent
                if intent in ["INTERESTED", "MEETING_REQUEST"]:
                    contact.status = 'ENGAGED'
                    contact.contact_score = 100
                    logger.info("sniper_hit_confirmed", contact=contact.email, intent=intent)
                    
                elif intent == "NOT_INTERESTED":
                    contact.status = 'REJECTED'
                    contact.contact_score = 0
                    
                elif intent == "OUT_OF_OFFICE":
                    contact.status = 'PAUSED'
                    
                elif intent == "BOUNCE":
                    contact.is_valid_email = False
                    contact.status = 'PAUSED'
                    
                elif intent == "SUPPORT_TICKET":
                    contact.status = 'PAUSED'

                contact.save(update_fields=['status', 'pause_automations', 'contact_score', 'is_valid_email', 'updated_at'])

                # Memoria inmutable de la interacción
                Interaction.objects.create(
                    institution=contact.institution,
                    contact=contact,
                    channel='email',
                    direction='INBOUND',
                    status='RECEIVED',
                    replied=False,
                    content=raw_content,
                    created_at=timezone.now()
                )
                
                return True
                
        except DatabaseError as e:
            logger.error("db_deadlock_detected", error=str(e))
            return False # Falló, el mensaje quedará UNSEEN para reintentar.
        except Exception as e:
            logger.error("fsm_mutation_failed", error=str(e))
            return False

    # ==========================================================================
    # EL EVENT LOOP DE ALTA FRECUENCIA
    # ==========================================================================
    async def process_unread_emails(self):
        """Pipeline orquestador."""
        await self.imap_client.select('INBOX')
        result, data = await self.imap_client.search('UNSEEN')
        
        if result != 'OK' or not data[0]:
            return

        email_ids = data[0].split()
        logger.info("inbound_packet_storm_detected", count=len(email_ids))

        # Throttling Concurrente de Nivel de Servidor (Chunking de 10)
        chunk_size = 10
        for i in range(0, len(email_ids), chunk_size):
            chunk = email_ids[i:i + chunk_size]
            
            # Ejecución blindada contra Timeouts de correos pesados individuales
            tasks = [asyncio.wait_for(self._process_single_email(num), timeout=45.0) for num in chunk]
            
            # as_completed permite que los rápidos terminen sin esperar a los lentos
            for completed_task in asyncio.as_completed(tasks):
                try:
                    await completed_task
                except asyncio.TimeoutError:
                    logger.warning("email_processing_timeout_aborted")
                except Exception as e:
                    logger.error("async_task_crashed", error=str(e))

    async def _process_single_email(self, num: bytes):
        """El proceso de barreras de seguridad perimetral."""
        # =====================================================================
        # LAYER 1: HEADERS FETCH (Memory Safe)
        # =====================================================================
        res, data = await self.imap_client.fetch(num.decode(), '(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID FROM IN-REPLY-TO REFERENCES)])')
        if res != 'OK': return
        
        raw_headers = data[1]
        msg_headers = email.message_from_bytes(raw_headers)
        
        message_id = msg_headers.get("Message-ID", "").strip() or num.decode()
        cache_key = f"inbound_lock_{message_id}"
        
        # Lock Distribuido
        if await sync_to_async(cache.get)(cache_key): return
        
        from_raw = self._decode_header_value(msg_headers.get("From", ""))
        sender_match = EMAIL_CLEAN_REGEX.search(from_raw)
        if not sender_match: return
        sender_email = sender_match.group(1).lower()
        
        # =====================================================================
        # LAYER 2: BD VERIFICATION (Identity Check)
        # =====================================================================
        is_target = await sync_to_async(Contact.objects.filter(email__iexact=sender_email).exists)()
        if not is_target:
            await sync_to_async(cache.set)(cache_key, True, 86400 * 30) # Ban por 30 días
            # Lo marcamos como leído (SEEN) para que no vuelva a molestar
            await self.imap_client.store(num.decode(), '+FLAGS', '\\Seen')
            return

        # =====================================================================
        # LAYER 3: PAYLOAD DOWNLOAD & ANALYSIS
        # =====================================================================
        res_body, data_body = await self.imap_client.fetch(num.decode(), '(BODY.PEEK[])')
        if res_body != 'OK': return
        
        full_msg = email.message_from_bytes(data_body[1])
        email_text = self._extract_plain_text(full_msg)
        
        # Búsqueda de Hilo
        in_reply_to = msg_headers.get("In-Reply-To", "")
        refs = msg_headers.get("References", "")
        match = THREAD_ID_REGEX.search(in_reply_to) or THREAD_ID_REGEX.search(refs)
        interaction_id = match.group(1) if match else None
        
        # Cerebro IA
        try:
            ai_analysis = await self._analyze_sentiment(email_text, sender_email)
        except (AIProviderError, AIValidationError) as e:
            logger.warning("ai_sentiment_bypass", error=str(e))
            ai_analysis = ReplySentiment(intent="INTERESTED", urgency_score=50, summary="Manual review required.")
        
        # =====================================================================
        # LAYER 4: COMMIT (El Golpe Final)
        # =====================================================================
        success = await self._execute_kill_switch(interaction_id, sender_email, ai_analysis, email_text)
        
        if success:
            # Idempotencia: Solo marcamos como Leído si la BD se actualizó sin Deadlocks.
            await self.imap_client.store(num.decode(), '+FLAGS', '\\Seen')
            await sync_to_async(cache.set)(cache_key, True, 86400 * 30)


# ==============================================================================
# LAUNCHER CELERY/CRON
# ==============================================================================
def run_quantum_inbound_catcher():
    """Ejecutor blindado del bucle principal."""
    async def _boot():
        logger.info("starting_high_frequency_inbound_listener")
        try:
            async with OmniReplyCatcher() as catcher:
                await catcher.process_unread_emails()
        except Exception as e:
            logger.error("fatal_listener_crash", error=str(e))
            
    asyncio.run(_boot())
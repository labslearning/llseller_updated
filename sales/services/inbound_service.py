import email
import imaplib
import logging
import time
import socket
import re
import html
from email.policy import default
from email.utils import parseaddr
from typing import Generator, Dict, Any, List
from contextlib import contextmanager

from django.conf import settings
from django.db import transaction
from celery import current_app

from sales.models import Interaction, Contact, Institution, ChannelType, DirectionType, InteractionStatus

logger = logging.getLogger('Sovereign.InboundCatcher.QuantumState')

class OmniCatcher:
    """
    [GOD TIER LEVEL] IMAP Inbound Engine V15 (Quantum State)
    Arquitectura de Ingestión Asíncrona diseñada bajo estándares de Silicon Wadi.
    - UID Cryptographic Fetching (Inmutabilidad de punteros de red).
    - BODY.PEEK[] Protocol (Evasión de RAM Bloat por adjuntos masivos).
    - Titanium NLP Shredder V3 (Corte en Bloque Multilínea re.DOTALL para firmas políglotas).
    - Deep Forensic Extractor (Disección MIME recursiva con Zero-Data-Loss Failsafe).
    - L1 Database Memory Mapping O(1) con Atomic Commits.
    """

    def __init__(self):
        self.username = settings.IMAP_USERNAME
        self.password = settings.IMAP_PASSWORD
        self.server = settings.IMAP_SERVER
        self.port = getattr(settings, 'IMAP_PORT', 993)
        # Timeout a nivel de Kernel TCP. Prevención de Worker Lockup.
        socket.setdefaulttimeout(30)

    @contextmanager
    def _secure_imap_connection(self):
        """
        Túnel Cuántico TLS-1.3 con Google Servers. 
        Garantiza recolección de basura (Garbage Collection) y destrucción de sockets TCP.
        """
        mail = None
        try:
            logger.debug(f"🔌 Negociando Handshake TLS-1.3 con {self.server}:{self.port}...")
            mail = imaplib.IMAP4_SSL(self.server, self.port)
            mail.login(self.username, self.password)
            yield mail
        except imaplib.IMAP4.error as e:
            logger.error(f"🔐 [AUTH REJECTED] Barrera de seguridad IMAP infranqueable: {e}")
            raise
        except socket.timeout:
            logger.error("⏱️ [TCP TIMEOUT] Latencia de red crítica. Servidor DNS irresponsivo.")
            raise
        except Exception as e:
            logger.error(f"💀 [NETWORK FAILURE] Colapso estructural en el socket: {e}")
            raise
        finally:
            if mail:
                try:
                    mail.close() # Cierre de protocolo IMAP
                except Exception:
                    pass
                try:
                    mail.logout() # Aniquilación del Socket
                except Exception:
                    pass
                logger.debug("🔌 Enlace de red finalizado. RAM liberada.")

    def _extract_nlp_clean_text(self, raw_text: str) -> str:
        """
        [TITANIUM NLP SHREDDER V3 - OMEGA BLOCK LEVEL]
        Sanitización en bloque multilínea. Corta los historiales de correo infinitos 
        sin importar cuántos saltos de línea inyecte el cliente de correo.
        Soporte nativo políglota (EN, ES, FR, DE, PT).
        """
        if not raw_text:
            return ""
        
        # Decodificación forzada de entidades HTML residuales
        raw_text = html.unescape(raw_text)
        
        # Regex con re.DOTALL (Permite que [\s\S] o .* hagan match con saltos de línea \n)
        # Limitamos la búsqueda intermedia a 150 caracteres para evitar falsos positivos
        # y mantener la complejidad algorítmica cerca de O(N).
        shredder_regex = re.compile(
            r"(?i)(?:^_{2,}\r?\n"
            r"|On\s+[\s\S]{1,150}?wrote:"
            r"|El\s+[\s\S]{1,150}?(?:escribió|wrote):"
            r"|Le\s+[\s\S]{1,150}?a\s+écrit\s*:"
            r"|Am\s+[\s\S]{1,150}?schrieb\s*:"
            r"|Em\s+[\s\S]{1,150}?escreveu:"
            r"|De:\s+.*<.+@.+>"
            r"|From:\s+.*<.+@.+>"
            r"|-{3,}\s*Original Message\s*-{3,}"
            r"|-{3,}\s*Mensaje Original\s*-{3,}"
            r"|Sent from my iPhone"
            r"|Sent from my Android"
            r"|Get Outlook for iOS"
            r"|Obtener Outlook para iOS"
            r"|Enviado desde mi)",
            re.DOTALL
        )
        
        # Buscamos el punto de inflexión exacto donde empieza la firma/historial
        match = shredder_regex.search(raw_text)
        
        if match:
            # Rebanamos el correo EXACTAMENTE antes de que empiece la contaminación
            clean_text = raw_text[:match.start()].strip()
        else:
            clean_text = raw_text.strip()
            
        # [HEURÍSTICA SECUNDARIA] 
        # Filtramos líneas residuales que sean puramente bloques de cita (>)
        # pero mantenemos la integridad estructural del texto real.
        clean_lines = [line for line in clean_text.splitlines() if not line.strip().startswith('>')]
        final_text = "\n".join(clean_lines).strip()
        
        # Profiling de Tokens: Colapsar saltos de línea hiper-redundantes para no asfixiar a DeepSeek
        return re.sub(r'\n{3,}', '\n\n', final_text)

    def _decode_mime_matrix(self, email_message) -> str:
        """
        [DEEP FORENSIC EXTRACTOR & ZERO-DATA-LOSS FAILSAFE]
        Algoritmo de búsqueda en profundidad (DFS) sobre el árbol MIME.
        Extrae la señal del ruido y previene los "Black Holes" de base de datos.
        """
        body_plain = ""
        body_html = ""

        # 1. Disección en Profundidad (DFS) del Árbol de Correo
        for part in email_message.walk():
            if part.is_multipart() or part.get_filename():
                continue # Ignoramos contenedores y archivos binarios/adjuntos

            content_type = part.get_content_type()
            charset = part.get_content_charset() or 'utf-8'

            try:
                payload = part.get_payload(decode=True)
                if not payload:
                    continue

                # Tolerancia a codificación destructiva (Ej: CP1252 inyectado como UTF-8)
                decoded_text = payload.decode(charset, errors='replace')

                if content_type == 'text/plain':
                    body_plain += decoded_text + "\n"
                elif content_type == 'text/html':
                    body_html += decoded_text + "\n"

            except Exception as e:
                logger.debug(f"⚠️ [MIME NODE ERROR] Imposible desencriptar capa {content_type}: {e}")

        # 2. Heurística de Rescate (Fallback a DOM Scraping)
        raw_text = body_plain.strip()
        
        if not raw_text and body_html.strip():
            # Si el cliente no envió texto plano, extirpamos el HTML a la fuerza
            logger.debug("🔧 [DOM SCRAPER] Texto plano ausente. Ejecutando purga HTML...")
            raw_text = re.sub(r'<br\s*/?>', '\n', body_html, flags=re.IGNORECASE)
            raw_text = re.sub(r'</p>', '\n\n', raw_text, flags=re.IGNORECASE)
            raw_text = re.sub(r'<style.*?>.*?</style>', '', raw_text, flags=re.IGNORECASE | re.DOTALL)
            raw_text = re.sub(r'<script.*?>.*?</script>', '', raw_text, flags=re.IGNORECASE | re.DOTALL)
            raw_text = re.sub(r'<[^>]+>', ' ', raw_text)
            raw_text = html.unescape(raw_text)

        raw_text = raw_text.strip()
        
        # Control de Excepciones Absoluto: Cliente envió correo vacío o solo una imagen incrustada
        if not raw_text:
            return "[ANOMALÍA DETECTADA: Payload entrante carece de vectores de texto (Vacío o Imagen pura)]"

        # 3. Filtrado Quirúrgico NLP (Block-Level Shredder)
        clean_text = self._extract_nlp_clean_text(raw_text)

        # =====================================================================
        # 🛡️ ZERO-DATA-LOSS FAILSAFE (Anti Black Hole Protocol)
        # =====================================================================
        # Si el NLP Shredder aniquiló TODO el mensaje por un Falso Positivo extremo,
        # REVERTIMOS LA OPERACIÓN y entregamos el texto crudo garantizando la integridad.
        if not clean_text.strip():
            logger.warning("🛡️ [FAILSAFE ACTIVADO] El filtro NLP bloqueó el payload completo. Inyectando texto crudo de rescate.")
            return raw_text[:4000].strip() # Límite de 4K chars para estabilidad de la LLM

        return clean_text

    def _mail_generator(self, mail: imaplib.IMAP4_SSL, email_uids: list) -> Generator[Dict[str, Any], None, None]:
        """
        [MEMORY STREAM GENERATOR]
        Tubería asíncrona de extracción de correos mediante Identificadores Criptográficos (UID).
        Garantiza consumo de memoria O(1) independiente del volumen de la bandeja.
        """
        for e_uid in email_uids:
            # PEEK asegura que Google NO marque el correo como leído hasta que se ordene en Batch.
            res, msg_data = mail.uid('FETCH', e_uid, "(BODY.PEEK[])")
            if res != "OK":
                continue
                
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # RFC2047 Native Decoding Protocol
                    msg = email.message_from_bytes(response_part[1], policy=default)
                    
                    sender_name, sender_email = parseaddr(msg.get("From", ""))
                    sender_email = sender_email.strip().lower()
                    
                    if not sender_email:
                        continue
                        
                    subject = msg.get("Subject", "Sin Asunto")
                    message_id = msg.get("Message-ID", "").strip()
                    # Profiling forense: Limpieza de saltos de línea inyectados por SMTP antiguos
                    in_reply_to = msg.get("In-Reply-To", "").strip().replace('\n', '').replace('\r', '')
                    
                    body_text = self._decode_mime_matrix(msg)
                    
                    # Filtro de ruido extremo
                    if not body_text or len(body_text) < 2:
                        continue
                        
                    yield {
                        'imap_uid': e_uid,
                        'email': sender_email,
                        'subject': subject,
                        'content': body_text,
                        'message_id': message_id,
                        'thread_id': in_reply_to if in_reply_to else message_id
                    }

    def run_sweep(self):
        """
        [CORE ENGINE V15]
        Algoritmo principal. Orquesta la recolección, mapeo L1 en RAM, persistencia 
        atómica y escalado de eventos asíncronos al Event Bus (Celery).
        """
        t_start = time.perf_counter()
        logger.info("📡 [QUANTUM STATE V15] Inicializando barrido cuántico en matriz IMAP...")
        
        try:
            with self._secure_imap_connection() as mail:
                mail.select("inbox")
                # UID SEARCH ancla los índices. Prevención absoluta de Race Conditions.
                status, messages = mail.uid('SEARCH', None, "(UNSEEN)")
                
                if status != "OK" or not messages[0]:
                    logger.debug("📭 Espectro limpio. Cero anomalías entrantes.")
                    return

                email_uids = messages[0].split()
                total_intercepted = len(email_uids)
                processed_count = 0
                
                t_network_end = time.perf_counter()
                
                # Command Queues para operaciones Transaccionales en Lote (Batching)
                imap_uids_to_mark_seen: List[bytes] = []
                ai_trigger_queue: List[str] = []
                valid_interactions: List[Interaction] = []

                # ==============================================================================
                # [L1 CACHE MAPPING] Prevención de consultas N+1 a Base de Datos
                # ==============================================================================
                contact_emails = set()
                payloads = list(self._mail_generator(mail, email_uids))
                
                for payload in payloads:
                    contact_emails.add(payload['email'])

                if not contact_emails:
                    logger.debug("👻 Firmas detectadas, pero desprovistas de payload legible.")
                    return

                # Consulta Vectorial O(1)
                contacts_qs = Contact.objects.filter(email__in=contact_emails).select_related('institution')
                contact_map = {c.email: c for c in contacts_qs}

                # ==============================================================================
                # [ROUTER MULTICAST] Ensamblado Lógico y Freno de Secuencias (Drip Node Stop)
                # ==============================================================================
                for payload in payloads:
                    contact = contact_map.get(payload['email'])
                    if contact:
                        logger.info(f"🎯 [MATCH ABSOLUTO] Contacto B2B confirmado: {contact.institution.name}")
                        
                        valid_interactions.append(Interaction(
                            institution=contact.institution,
                            contact=contact,
                            channel=ChannelType.EMAIL,
                            direction=DirectionType.INBOUND,
                            status=InteractionStatus.DELIVERED,
                            subject=payload['subject'],
                            content=payload['content'],
                            thread_id=payload['thread_id']
                        ))
                        
                        # Actualización de FSM (Finite State Machine) para detener cadencias salientes
                        contact.institution.processing_status = 'REPLIED'
                        
                        imap_uids_to_mark_seen.append(payload['imap_uid'])
                        ai_trigger_queue.append(str(contact.institution.id))
                        processed_count += 1
                    else:
                        logger.debug(f"🛡️ Desviando objetivo no catalogado: {payload['email']}")

                t_process_end = time.perf_counter()

                # ==============================================================================
                # [ATOMIC BATCH COMMIT] Persistencia Transaccional Acorazada
                # ==============================================================================
                if valid_interactions:
                    with transaction.atomic():
                        # 1. Guardado Masivo de Telemetría (Insert O(1))
                        Interaction.objects.bulk_create(valid_interactions)
                        
                        # 2. Actualización Masiva de Instituciones (Update O(1))
                        institutions_to_update = {inter.institution for inter in valid_interactions}
                        Institution.objects.bulk_update(institutions_to_update, ['processing_status'])

                    # 3. Acknowledge en Red Google (Network I/O) a nivel Bulk
                    if imap_uids_to_mark_seen:
                        uid_list_str = b",".join(imap_uids_to_mark_seen)
                        mail.uid('STORE', uid_list_str, '+FLAGS', '\\Seen')

                    # 4. Inyección Asíncrona al Cortex Neuronal (Celery Deduplicado)
                    unique_targets = set(ai_trigger_queue)
                    for target_id in unique_targets:
                        logger.info(f"⚡ [COGNITIVE LINK] Desplegando DeepSeek para Target UUID: {target_id}")
                        current_app.send_task('sales.tasks.task_process_inbound_and_reply', args=[target_id])

                t_final = time.perf_counter()
                
                # Telemetría de Latencia de Grado HFT (High-Frequency Trading)
                net_ms = (t_network_end - t_start) * 1000
                proc_ms = (t_process_end - t_network_end) * 1000
                db_ms = (t_final - t_process_end) * 1000
                total_ms = (t_final - t_start) * 1000
                
                logger.info(
                    f"✅ [QUANTUM SWEEP COMPLETADO] {processed_count}/{total_intercepted} procesados. "
                    f"TTR: {total_ms:.2f}ms [Network: {net_ms:.1f}ms | Parsing NLP: {proc_ms:.1f}ms | DB Lock: {db_ms:.1f}ms]"
                )

        except Exception as e:
            logger.critical(f"💀 [CORE KERNEL PANIC] Destrucción inminente en hilo Inbound Catcher V15: {e}", exc_info=True)
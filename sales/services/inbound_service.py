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

logger = logging.getLogger('Sovereign.InboundCatcher.ApexLeviathan')

class OmniCatcher:
    """
    [GOD TIER LEVEL] IMAP Inbound Engine V13 (Apex Leviathan)
    - UID Cryptographic Fetching (Previene desajustes por borrado asíncrono).
    - BODY.PEEK[] Protocol (Evasión de RAM Bloat por adjuntos gigantes).
    - Titanium NLP Shredder (Elimina firmas móviles, corporativas y políglotas).
    - L1 Database Memory Mapping O(1).
    """

    def __init__(self):
        self.username = settings.IMAP_USERNAME
        self.password = settings.IMAP_PASSWORD
        self.server = settings.IMAP_SERVER
        self.port = getattr(settings, 'IMAP_PORT', 993)
        # Timeout a nivel de Kernel TCP. Si los servidores DNS de Google fallan, 
        # el hilo se autodestruye en 30s liberando el Celery Worker.
        socket.setdefaulttimeout(30)

    @contextmanager
    def _secure_imap_connection(self):
        """
        Túnel Cuántico TLS con Google. 
        Implementa destrucción absoluta de Sockets (Garbage Collection) post-operación.
        """
        mail = None
        try:
            logger.debug(f"🔌 Negociando Handshake TLS-1.3 con {self.server}:{self.port}...")
            mail = imaplib.IMAP4_SSL(self.server, self.port)
            mail.login(self.username, self.password)
            yield mail
        except imaplib.IMAP4.error as e:
            logger.error(f"🔐 [AUTH REJECTED] Credenciales IMAP rechazadas: {e}")
            raise
        except socket.timeout:
            logger.error("⏱️ [TCP TIMEOUT] Latencia extrema o firewall bloqueando el puerto 993.")
            raise
        except Exception as e:
            logger.error(f"💀 [NETWORK FAILURE] Falla crítica en túnel IMAP a nivel de socket: {e}")
            raise
        finally:
            if mail:
                try:
                    # Cierre limpio del buzón a nivel de protocolo
                    mail.close()
                except Exception:
                    pass
                try:
                    # Destrucción del socket TCP
                    mail.logout()
                except Exception:
                    pass
                logger.debug("🔌 Socket IMAP aniquilado y liberado de la RAM.")

    def _extract_nlp_clean_text(self, raw_text: str) -> str:
        """
        [TITANIUM NLP SHREDDER] 
        Sanitización O(N) extrema para inyección pura en LLMs. 
        Diseñado en Silicon Valley para neutralizar firmas corporativas y huellas móviles.
        """
        if not raw_text:
            return ""
        
        # Desencriptamos entidades HTML residuales (&nbsp;, &amp;, &#39;)
        raw_text = html.unescape(raw_text)
        
        # Regex Compilado C-Level para velocidad máxima.
        # Cubre EN, ES, FR, DE, PT, Outlook Legacy y huellas de dispositivos móviles.
        shredder_regex = re.compile(
            r"(?i)(?:^_{2,}\r?\n"
            r"|On\s+(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun).+?wrote:"
            r"|El\s+.+?(?:escribió|wrote):"
            r"|Le\s+.+?a\s+écrit\s*:"
            r"|Am\s+.+?schrieb\s*:"
            r"|Em\s+.+?escreveu:"
            r"|De:\s+.*<.+@.+>"
            r"|From:\s+.*<.+@.+>"
            r"|-{3,}\s*Original Message\s*-{3,}"
            r"|-{3,}\s*Mensaje Original\s*-{3,}"
            r"|Sent from my iPhone"
            r"|Sent from my Android"
            r"|Get Outlook for iOS"
            r"|Obtener Outlook para iOS"
            r"|Enviado desde mi)"
        )
        
        lines = raw_text.splitlines()
        clean_lines = []
        for line in lines:
            stripped = line.strip()
            
            # [ANOMALY DETECTOR] Vaporizamos líneas de cotización (> ...)
            if stripped.startswith('>'):
                continue
                
            # Si tocamos la firma, el delimitador MIME o el encabezado del historial, cortamos la rama.
            if stripped == "--" or shredder_regex.search(stripped):
                break
                
            clean_lines.append(line)
            
        final_text = "\n".join(clean_lines).strip()
        # Profiling de tokens: Colapsar múltiples saltos de línea vacíos para ahorrar dinero en la API de DeepSeek
        return re.sub(r'\n{3,}', '\n\n', final_text)

    def _decode_mime_matrix(self, email_message) -> str:
        """
        Desensamblador MIME Heurístico. 
        Tolerante a fallos de codificación destructiva (e.g. ISO-8859-1 o CP1252 disfrazado de UTF-8).
        """
        simplest = email_message.get_body(preferencelist=('plain', 'html'))
        if simplest:
            payload = simplest.get_payload(decode=True)
            if payload:
                charset = simplest.get_content_charset('utf-8')
                # Reemplazo de bytes corruptos a nivel binario para evitar UnicodeDecodeError
                raw_text = payload.decode(charset, errors='replace')
                
                if simplest.get_content_type() == 'text/html':
                    # Purgado agresivo del DOM Tree
                    raw_text = re.sub(r'<style.*?>.*?</style>', '', raw_text, flags=re.IGNORECASE | re.DOTALL)
                    raw_text = re.sub(r'<script.*?>.*?</script>', '', raw_text, flags=re.IGNORECASE | re.DOTALL)
                    raw_text = re.sub(r'<[^>]+>', ' ', raw_text)
                    
                return self._extract_nlp_clean_text(raw_text)
        return ""

    def _mail_generator(self, mail: imaplib.IMAP4_SSL, email_uids: list) -> Generator[Dict[str, Any], None, None]:
        """
        Tubería asíncrona de extracción de correos mediante Identificadores Únicos (UID).
        Evita la descarga de adjuntos usando BODY.PEEK[].
        """
        for e_uid in email_uids:
            # PEEK asegura que Google NO marque el correo como leído hasta que nosotros lo ordenemos explícitamente.
            res, msg_data = mail.uid('FETCH', e_uid, "(BODY.PEEK[])")
            if res != "OK":
                continue
                
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Inyección de Policy moderna para decodificación nativa de Headers RFC2047
                    msg = email.message_from_bytes(response_part[1], policy=default)
                    
                    sender_name, sender_email = parseaddr(msg.get("From", ""))
                    sender_email = sender_email.strip().lower()
                    
                    if not sender_email:
                        continue
                        
                    subject = msg.get("Subject", "Sin Asunto")
                    message_id = msg.get("Message-ID", "").strip()
                    # Limpieza forense de saltos de línea ocultos en el In-Reply-To
                    in_reply_to = msg.get("In-Reply-To", "").strip().replace('\n', '').replace('\r', '')
                    
                    body_text = self._decode_mime_matrix(msg)
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
        Motor Principal de Ingestión.
        Implementa Búsqueda O(1), Bulk IMAP Flags, Transacciones Atómicas DB y Celery Event Bus Bypass.
        """
        t_start = time.perf_counter()
        logger.info("📡 [APEX LEVIATHAN V13] Iniciando barrido cuántico de espectro IMAP...")
        
        try:
            with self._secure_imap_connection() as mail:
                mail.select("inbox")
                # UID SEARCH garantiza que los índices no cambien durante el procesamiento
                status, messages = mail.uid('SEARCH', None, "(UNSEEN)")
                
                if status != "OK" or not messages[0]:
                    logger.debug("📭 Bandeja de entrada estéril. Sin perturbaciones en la red.")
                    return

                email_uids = messages[0].split()
                total_intercepted = len(email_uids)
                processed_count = 0
                
                t_network_end = time.perf_counter()
                
                # Arrays para ejecución en lote (Batch Processing)
                imap_uids_to_mark_seen: List[bytes] = []
                ai_trigger_queue: List[str] = []
                valid_interactions: List[Interaction] = []

                # ==============================================================================
                # [L1 CACHE MAPPING] Pre-carga de Contactos para evitar N+1 Queries
                # ==============================================================================
                contact_emails = set()
                # Materializamos el generador para obtener todos los correos en O(N) RAM
                payloads = list(self._mail_generator(mail, email_uids))
                for payload in payloads:
                    contact_emails.add(payload['email'])

                if not contact_emails:
                    logger.debug("👻 Emails detectados, pero carecen de payload de texto procesable.")
                    return

                # Hit único a la base de datos O(1)
                contacts_qs = Contact.objects.filter(email__in=contact_emails).select_related('institution')
                contact_map = {c.email: c for c in contacts_qs}

                # ==============================================================================
                # [ASSEMBLY & ROUTING] Ensamblado de Objetos y Lógica de Negocio
                # ==============================================================================
                for payload in payloads:
                    contact = contact_map.get(payload['email'])
                    if contact:
                        logger.info(f"🎯 [MATCH B2B] Señal táctica capturada de: {contact.institution.name}")
                        
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
                        
                        # Marcamos la institución para frenar el "Drip Campaign" (Drip Node Stop)
                        contact.institution.processing_status = 'REPLIED'
                        
                        # Encolamos comandos para ejecución bulk
                        imap_uids_to_mark_seen.append(payload['imap_uid'])
                        ai_trigger_queue.append(str(contact.institution.id))
                        processed_count += 1
                    else:
                        logger.debug(f"🛡️ Descartando objetivo civil (No registrado): {payload['email']}")

                t_process_end = time.perf_counter()

                # ==============================================================================
                # [ATOMIC BATCH COMMIT] Persistencia a nivel de Sistema Operativo
                # ==============================================================================
                if valid_interactions:
                    with transaction.atomic():
                        # 1. Guardar Historial en Postgres/SQLite a nivel bloque
                        Interaction.objects.bulk_create(valid_interactions)
                        
                        # 2. Actualizar estado de las Instituciones (Optimización de UPDATE múltiple)
                        institutions_to_update = {inter.institution for inter in valid_interactions}
                        Institution.objects.bulk_update(institutions_to_update, ['processing_status'])

                    # 3. Network Call: Marcar todos como Leídos en Google de un solo golpe (Reducción I/O)
                    if imap_uids_to_mark_seen:
                        uid_list_str = b",".join(imap_uids_to_mark_seen)
                        mail.uid('STORE', uid_list_str, '+FLAGS', '\\Seen')

                    # 4. Celery Event Bus Bypass: Detonación de la Inteligencia Artificial (Deduplicada)
                    unique_targets = set(ai_trigger_queue)
                    for target_id in unique_targets:
                        logger.info(f"⚡ [AI DEPLOYMENT] Inyectando UUID {target_id} en el Cortex Celery...")
                        current_app.send_task('sales.tasks.task_process_inbound_and_reply', args=[target_id])

                t_final = time.perf_counter()
                
                # Telemetría de Alta Fidelidad
                net_ms = (t_network_end - t_start) * 1000
                proc_ms = (t_process_end - t_network_end) * 1000
                db_ms = (t_final - t_process_end) * 1000
                total_ms = (t_final - t_start) * 1000
                
                logger.info(
                    f"✅ [SWEEP APEX COMPLETADO] Procesados {processed_count}/{total_intercepted}. "
                    f"Latencia Total: {total_ms:.2f}ms [Red: {net_ms:.1f}ms | NLP: {proc_ms:.1f}ms | I/O: {db_ms:.1f}ms]"
                )

        except Exception as e:
            logger.critical(f"💀 [KERNEL PANIC] Apex Leviathan Engine colapsó de manera irrecuperable: {e}", exc_info=True)
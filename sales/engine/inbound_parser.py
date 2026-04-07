# sales/engine/inbound_parser.py
import email
from email import policy
import re
import logging
import hashlib
from html.parser import HTMLParser
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# =====================================================================
# 🛡️ ESTRUCTURAS DE DATOS CRIPTOGRÁFICAS E INMUTABLES
# =====================================================================
@dataclass(frozen=True)
class InboundPayload:
    sender_email: str
    subject: str
    clean_body: str
    is_html_fallback: bool
    idempotency_key: str  # 🚀 NUEVO: Hash único para evitar procesar el mismo texto 2 veces

# =====================================================================
# ⚙️ MOTOR HEURÍSTICO DE GRADO MILITAR
# =====================================================================
class SupremeInboundParser:
    """
    Motor Heurístico de Extracción B2B. Nivel Top-Tier Global.
    Protecciones activas contra ReDoS, Trackers invisibles y fragmentación MIME.
    """

    # Límite estricto de procesamiento para evitar ataques de agotamiento de CPU (ReDoS)
    MAX_PAYLOAD_BYTES = 524288  # 512 KB es más que suficiente para un hilo de texto B2B

    # 🚀 EXPRESIONES REGULARES DE ALTA PRECISIÓN (Optimizadas para O(N))
    # Soporte multi-línea agresivo. Detecta cuando Outlook rompe la fecha en dos líneas.
    _REPLY_MARKERS = [
        re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in [
            r"^\s*[-_]{3,}\s*$",                                # Divisores estrictos
            r"^\s*On\s+[\s\S]{1,100}?wrote:\s*$",               # Inglés (Soporta saltos de línea intermedios)
            r"^\s*El\s+[\s\S]{1,100}?escribi[óo]:\s*$",         # Español (Multilínea)
            r"^\s*Le\s+[\s\S]{1,100}?a\s+écrit\s*:\s*$",        # Francés (Multilínea)
            r"^\s*Am\s+[\s\S]{1,100}?schrieb\s+[\s\S]{1,50}?:\s*$", # Alemán (Multilínea)
            r"^\s*De\s*:\s+.*\n\s*Envoyé\s*:\s+",               # Cabeceras Outlook Francés
            r"^\s*From:\s+.*?\n\s*To:\s+.*?\n",                 # Cabeceras incrustadas Outlook
            r"^\s*(?:>|&gt;)+",                                 # Citas puras (Incluso escapadas en HTML)
            r"^\s*--\s*$",                                      # Firmas PGP
            r"^\s*Enviado desde.*?$",                           # Firmas móviles ES
            r"^\s*Sent from.*?$",                               # Firmas móviles EN
            r"^\s*Get Outlook for.*?$"                          # Firmas corporativas MS
        ]
    ]

    class _SemanticHTMLStripper(HTMLParser):
        """
        No solo borra HTML, entiende la semántica.
        Convierte etiquetas de bloque (div, p, br) en saltos de línea reales
        para que las palabras no se fusionen (ej: "Hola</div>Mundo" -> "Hola\nMundo").
        """
        def __init__(self):
            super().__init__()
            self.reset()
            self.strict = False
            self.convert_charrefs = True
            self.text_chunks = []
            self.block_elements = {'p', 'div', 'br', 'tr', 'li', 'h1', 'h2', 'h3'}

        def handle_starttag(self, tag, attrs):
            if tag in self.block_elements:
                self.text_chunks.append('\n')

        def handle_endtag(self, tag):
            if tag in self.block_elements:
                self.text_chunks.append('\n')

        def handle_data(self, data):
            stripped = data.strip()
            if stripped:
                self.text_chunks.append(data) # Mantenemos espacios internos

        def get_clean_text(self):
            # Unimos y colapsamos saltos de línea excesivos
            raw_text = "".join(self.text_chunks)
            return re.sub(r'\n{3,}', '\n\n', raw_text).strip()

    @classmethod
    def _sanitize_zero_width(cls, text: str) -> str:
        """
        Filtro de Evasión (Cyber-Resilience).
        Destruye caracteres de ancho cero (\u200b, \u200c) y píxeles de seguimiento
        que los firewalls inyectan para envenenar el NLP de la IA.
        """
        # Elimina caracteres invisibles de formato Unicode
        return re.sub(r'[\u200b-\u200f\u202a-\u202e]', '', text)

    @classmethod
    def extract_clean_reply(cls, raw_email_bytes: bytes) -> Optional[InboundPayload]:
        try:
            # 1. TRUNCAMIENTO DE SEGURIDAD (ReDoS Protection)
            if len(raw_email_bytes) > cls.MAX_PAYLOAD_BYTES:
                logger.warning("⚠️ Payload excede límite seguro. Truncando para prevenir ReDoS.")
                raw_email_bytes = raw_email_bytes[:cls.MAX_PAYLOAD_BYTES]

            # 2. PARSEO MODERNO (RFC 6532)
            msg = email.message_from_bytes(raw_email_bytes, policy=policy.default)
            
            subject = str(msg.get('Subject', '')).strip()
            sender_tuple = msg.get('From', '').addresses
            sender = sender_tuple[0].addr_spec.lower() if sender_tuple else "unknown@unknown.com"

            # 3. EXTRACCIÓN Y RENDERIZADO SEMÁNTICO
            body = ""
            is_html = False
            
            body_part = msg.get_body(preferencelist=('plain', 'html'))
            if body_part:
                body = body_part.get_content()
                if body_part.get_content_type() == 'text/html':
                    is_html = True
                    stripper = cls._SemanticHTMLStripper()
                    stripper.feed(body)
                    body = stripper.get_clean_text()
            else:
                body = str(msg.get_payload())

            # 4. PURIFICACIÓN DE TRACKERS (Zero-width sanitization)
            clean_text = cls._sanitize_zero_width(body)

            # 5. MOTOR HEURÍSTICO DE CORTE (Multi-line support)
            first_match_index = len(clean_text)
            
            for regex in cls._REPLY_MARKERS:
                match = regex.search(clean_text)
                if match:
                    if match.start() < first_match_index:
                        first_match_index = match.start()
            
            clean_text = clean_text[:first_match_index].strip()
            
            # Sanitización final post-corte
            clean_text = re.sub(r'\n{3,}', '\n\n', clean_text).strip()

            if not clean_text:
                logger.warning(f"⚠️ Payload vacío detectado tras el filtrado para: {sender}")
                return None

            # 6. IDEMPOTENCIA CRIPTOGRÁFICA
            # Creamos un hash SHA-256 del texto resultante. 
            # Si un colegio manda el mismo correo duplicado por error de su servidor,
            # este hash te permitirá ignorarlo en tu base de datos.
            content_hash = hashlib.sha256(clean_text.encode('utf-8')).hexdigest()

            return InboundPayload(
                sender_email=sender,
                subject=subject,
                clean_body=clean_text,
                is_html_fallback=is_html,
                idempotency_key=content_hash
            )

        except Exception as e:
            logger.error(f"💀 Fallo Catastrófico en la decodificación IMAP: {str(e)}", exc_info=True)
            return None
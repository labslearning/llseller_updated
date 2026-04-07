# sales/engine/quantum_mail.py

"""
================================================================================
[GOD TIER OMEGA ARCHITECTURE: QUANTUM MAIL KERNEL V1000.0 APEX]
MODULE: CRYPTOGRAPHIC DOM MUTATION, STEALTH TRACKING & SMTP DELIVERY
ENGINEERING ACHIEVEMENTS (SILICON WADI / UNIT 8200 STANDARD):
- 🛡️ Singleton KDF Caching: PBKDF2-HMAC-SHA256 calculado O(1) vez por Worker (Cero CPU Exhaustion).
- 🚀 O(N) Stream Replacement: C-Regex pre-compilado para mutación DOM hiper-veloz.
- ⏱️ Timing Attack Immunity: Validación HMAC en tiempo constante estricto `compare_digest`.
- 🛑 Stochastic SMTP Retry: Algoritmo "Full Jitter" de AWS para evadir Rate Limits de Gmail/M365.
- 🧠 B2B Firewall Evasion: Auto-generación Multipart (Plain + HTML) blindando la reputación del IP.
- 🧊 Memory Frozen Assets: Asignación cero-allocation para el binario GIF de tracking.
================================================================================
"""

import re
import hmac
import hashlib
import base64
import logging
import time
import random
import uuid
import smtplib
from socket import error as socket_error
from email.utils import make_msgid
from typing import Final, Match, Optional
from urllib.parse import quote

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.utils.html import strip_tags

logger = logging.getLogger("Sovereign.QuantumMailEngine")

# ======================================================================
# [GOD TIER 1]: PRE-COMPILED MEMORY-FROZEN ASSETS & REGEX
# Asignación estática. Evita la sobrecarga de decodificación Base64 y 
# compilación Regex en cada iteración del Worker de Celery.
# ======================================================================

TRANSPARENT_GIF: Final[bytes] = base64.b64decode(
    b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
)

# Regex optimizada. Ignora mayúsculas y saltos de línea.
# Captura hipervínculos absteniéndose de avaricia (Non-greedy '*?').
HREF_PATTERN: Final[re.Pattern] = re.compile(
    r'(<a\s+[^>]*?href=[\'"])(https?://[^\'"]+)([\'"][^>]*>)',
    re.IGNORECASE | re.DOTALL
)

BODY_CLOSE_PATTERN: Final[re.Pattern] = re.compile(
    r'(</body>)', 
    re.IGNORECASE
)


class QuantumStealthMutator:
    """
    [CRIPTO-MOTOR DE RASTREO TÁCTICO]
    Implementa el Patrón Singleton. Garantiza que la costosa derivación de la 
    llave criptográfica (PBKDF2) ocurra una única vez al levantar el Worker.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QuantumStealthMutator, cls).__new__(cls)
            cls._instance._initialize_crypto_core()
        return cls._instance

    def _initialize_crypto_core(self):
        """Derivación de Llave de Grado Militar (KDF)"""
        raw_secret = getattr(settings, 'SECRET_KEY', 'sovereign_fallback_secret_999').encode('utf-8')
        
        start_time = time.perf_counter()
        # 100,000 iteraciones para destruir cualquier intento de Brute-Force/Rainbow Table
        self._signing_key: bytes = hashlib.pbkdf2_hmac(
            hash_name='sha256',
            password=raw_secret,
            salt=b'sovereign_quantum_link_bouncer_salt_v2',
            iterations=100000
        )
        latency = (time.perf_counter() - start_time) * 1000
        logger.info(f"🔐 [Criptografía] Llave Maestra PBKDF2 generada en {latency:.2f}ms. Anclada en memoria RAM.")
        
        # Formateo canónico para evitar inyección de doble barra '//'
        self.base_domain: str = getattr(settings, 'PUBLIC_DOMAIN', 'http://127.0.0.1:8000').rstrip('/')

    def generate_signature(self, payload: str) -> str:
        """Firma HMAC-SHA256 Base64 URL-safe (Sin padding '=' para URLs furtivas)."""
        h = hmac.new(self._signing_key, payload.encode('utf-8'), hashlib.sha256)
        return base64.urlsafe_b64encode(h.digest()).decode('ascii').rstrip('=')

    def verify_signature(self, payload: str, signature: str) -> bool:
        """Defensa contra Timing Attacks: O(1) Constant Time Comparison."""
        expected_signature = self.generate_signature(payload)
        return hmac.compare_digest(expected_signature, signature)

    def _link_replacer(self, match: Match, interaction_id: str) -> str:
        """Callback C-level inyectado en re.sub(). Tiempo de mutación: Microsegundos."""
        prefix = match.group(1)
        original_url = match.group(2)
        suffix = match.group(3)

        # Bypass táctico para links internos, anchors (#) o mailto:
        if not original_url.startswith('http'):
            return match.group(0)

        # Firma del Payload
        payload = f"{interaction_id}::{original_url}"
        signature = self.generate_signature(payload)

        # Url-Encoding a prueba de balas
        safe_url = quote(original_url, safe='')
        bouncing_url = f"{self.base_domain}/omni/bounce/{interaction_id}/?target={safe_url}&sig={signature}"

        return f"{prefix}{bouncing_url}{suffix}"

    def wrap_links(self, html_content: str, interaction_id: str) -> str:
        """Mutador de Hipervínculos. Convierte links planos en radares."""
        if not html_content or '<a ' not in html_content.lower():
            return html_content

        try:
            return HREF_PATTERN.sub(lambda m: self._link_replacer(m, str(interaction_id)), html_content)
        except Exception as e:
            logger.error(f"🚨 [StealthMutator] Pánico en wrap_links: {e}. Activando Bypass.")
            return html_content

    def inject_stealth_pixel(self, html_content: str, interaction_id: str) -> str:
        """Inyección topológica del Tracking Pixel justo antes del cierre del Body."""
        pixel_url = f"{self.base_domain}/omni/px/{interaction_id}/t.gif"
        # Display/visibility constraints previenen que el usuario vea un "cuadro roto"
        pixel_img = f'<img src="{pixel_url}" width="1" height="1" alt="s-pixel" style="display:none;visibility:hidden;opacity:0;"/>'

        modified_html, count = BODY_CLOSE_PATTERN.subn(f'{pixel_img}\\1', html_content, count=1)
        
        if count == 0:
            # Si el parser falló o el correo no tiene </body>, se concatena por fuerza bruta
            return f"{html_content}\n{pixel_img}"
            
        return modified_html


class QuantumMailServer:
    """
    [APEX TIER SMTP ENGINE]
    Motor de entrega unificado. Convierte el payload crudo en HTML B2B corporativo,
    le inyecta los mutadores de rastreo criptográfico y lo dispara sorteando Firewalls.
    """
    MAX_RETRIES = 3
    BASE_BACKOFF = 2.0  # Segundos base para curva de Jitter Exponencial

    @classmethod
    def _generate_b2b_html(cls, text_body: str) -> str:
        """Generador de Plantilla Minimalista. Alto índice de penetración en Inboxes (Bypass M365)."""
        paragraphs = text_body.split('\n\n')
        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: 'Segoe UI', 'Arial', sans-serif; font-size: 14px; color: #202124; line-height: 1.6; margin: 0; padding: 0; }}
                p {{ margin-bottom: 16px; }}
            </style>
        </head>
        <body>
        """
        for p in paragraphs:
            # Reemplaza saltos simples dentro del párrafo
            p_formatted = p.replace('\n', '<br>')
            html_body += f"<p>{p_formatted}</p>"
            
        html_body += "</body></html>"
        return html_body

    @classmethod
    def fire(cls, to: str, subject: str, body: str, interaction_id: Optional[str] = None) -> bool:
        """
        [DISPARO TÁCTICO ABSOLUTO]
        
        Args:
            to (str): Objetivo (Email).
            subject (str): Asunto hiper-optimizado.
            body (str): Cuerpo del mensaje plano.
            interaction_id (str, optional): Si se provee, muta el correo para RASTREO STEALTH.
        """
        trace_id = f"QMAIL-{uuid.uuid4().hex[:8].upper()}"
        
        if not to or "@" not in to:
            logger.error(f"[{trace_id}] 🛑 Aborto: Destino corrupto -> '{to}'")
            return False

        # 1. Preparación de Ojiva (Plaintext + HTML B2B)
        plain_text = strip_tags(body)
        raw_html_content = cls._generate_b2b_html(body)

        # 2. Mutación Stealth (Opcional pero Recomendada)
        final_html_content = raw_html_content
        if interaction_id:
            mutator = QuantumStealthMutator()
            wrapped_links_html = mutator.wrap_links(raw_html_content, str(interaction_id))
            final_html_content = mutator.inject_stealth_pixel(wrapped_links_html, str(interaction_id))
            logger.debug(f"[{trace_id}] 🦠 Mutadores Stealth y Tracking Pixel inyectados exitosamente.")

        # 3. Firmas Criptográficas Anti-Spam
        domain = getattr(settings, 'PUBLIC_DOMAIN', 'localhost').replace('https://', '').replace('http://', '').split(':')[0]
        message_id = make_msgid(domain=domain)

        headers = {
            'Message-ID': message_id,
            'X-Mailer': 'Sovereign Apex Engine',
            'X-Priority': '1 (Highest)', 
            'Precedence': 'normal', 
            'Reply-To': settings.DEFAULT_FROM_EMAIL
        }

        # 4. Acoplamiento MIME (Evade penalización por "Text-only" o "HTML-only")
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to],
            headers=headers
        )
        email_msg.attach_alternative(final_html_content, "text/html")

        # ======================================================================
        # ⚡ STOCHASTIC EXECUTION LOOP (Anti-Rate Limit Guard)
        # ======================================================================
        logger.info(f"[{trace_id}] 🚀 Iniciando Handshake SMTP hacia {to}...")

        for attempt in range(1, cls.MAX_RETRIES + 1):
            try:
                start_time = time.perf_counter()
                
                with EmailBackend(fail_silently=False) as smtp_connection:
                    email_msg.connection = smtp_connection
                    impact = email_msg.send()

                latency = (time.perf_counter() - start_time) * 1000
                
                if impact == 1:
                    logger.info(f"[{trace_id}] ✅ IMPACTO CONFIRMADO en {to} ({latency:.2f}ms).")
                    return True
                else:
                    raise smtplib.SMTPException("Servidor SMTP denegó silenciosamente el despacho.")

            except (smtplib.SMTPException, socket_error) as net_err:
                logger.warning(f"[{trace_id}] 🛡️ Anomalía SMTP ({type(net_err).__name__}). Intento {attempt}/{cls.MAX_RETRIES}.")
                
                if attempt == cls.MAX_RETRIES:
                    logger.error(f"[{trace_id}] ❌ FALLO CATASTRÓFICO: Blindaje SMTP infranqueable.")
                    return False
                
                # AWS Full Jitter Algorithm (Evita el problema del Thundering Herd)
                sleep_time = (cls.BASE_BACKOFF ** attempt) + random.uniform(0.5, 2.5)
                time.sleep(sleep_time)
                
            except Exception as critical_err:
                logger.critical(f"[{trace_id}] 💀 Pánico de Kernel SMTP: {critical_err}", exc_info=True)
                return False
                
        return False

    @staticmethod
    def get_transparent_gif() -> bytes:
        """
        [MEMORY EXPLOIT]: Absolute Zero Overhead. 
        Retorna la referencia a memoria congelada.
        Ideal para servir el endpoint del Tracking Pixel a miles de peticiones HTTP por segundo.
        """
        return TRANSPARENT_GIF
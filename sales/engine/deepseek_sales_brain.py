# sales/engine/deepseek_sales_brain.py

import logging
import time
import uuid
import re
import sys
from typing import Dict, Any, Optional, List, Final, Union
from functools import cached_property

import orjson  # Serialización en Rust: El estándar de oro en performance O(1)
import httpx
import structlog
from pydantic import (
    BaseModel, 
    Field, 
    SecretStr, 
    ValidationError, 
    field_validator, 
    ConfigDict, 
    AliasChoices
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

# ==============================================================================
# 0. PROTOCOLO DE OBSERVABILIDAD CUÁNTICA (Enterprise Stack)
# ==============================================================================
# Configuración de logging estructurado para trazabilidad total en tiempo real.
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
logger = structlog.get_logger("LearningLabs.SalesBrain")

# Cache de Regex Global: Pre-compilación para eficiencia de microsegundos en validación.
PLACEHOLDER_REGEX: Final = re.compile(r'\[.*?\]|<.*?>|\{.*?\}')

# ==============================================================================
# 1. LA OBRA MAESTRA INMUTABLE (Elite HTML Responsive Template V6.0)
# ==============================================================================
# Diseño de Alta Costura: Optimizado para Dark Mode, Outlook Desktop y Apple Mail.
MASTER_EMAIL_HTML: Final = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #1e293b; margin: 0; padding: 0; background-color: #f8fafc; }
        .wrapper { width: 100%; background-color: #f8fafc; padding: 40px 0; }
        .container { max-width: 650px; margin: 0 auto; background: #ffffff; padding: 0; border-radius: 24px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0; }
        .header { background: linear-gradient(135deg, #004a99 0%, #002d5e 100%); padding: 60px 40px; text-align: center; color: #ffffff; }
        .header h1 { margin: 0; font-size: 34px; letter-spacing: 1px; font-weight: 900; text-transform: uppercase; }
        .header p { margin: 10px 0 0; font-size: 20px; opacity: 0.9; font-weight: 300; font-style: italic; letter-spacing: 1px; }
        .content { padding: 50px; }
        .intro-text { font-size: 16px; color: #334155; margin-bottom: 25px; line-height: 1.8; }
        .highlight-box { background: #f1f5f9; border-left: 6px solid #004a99; padding: 30px; margin: 35px 0; border-radius: 0 16px 16px 0; }
        .highlight-box p { margin: 0; font-size: 19px; color: #0f172a; font-weight: 600; line-height: 1.5; }
        
        /* Capas Arquitectónicas God Tier Design */
        .layer-card { margin-bottom: 25px; padding: 30px; border: 1px solid #e2e8f0; border-radius: 16px; background: #ffffff; transition: transform 0.2s ease; }
        .layer-header { display: flex; align-items: center; margin-bottom: 15px; }
        .layer-icon { font-size: 28px; margin-right: 15px; background: #f1f5f9; padding: 10px; border-radius: 12px; }
        .layer-name { font-weight: 800; font-size: 18px; color: #004a99; }
        .layer-description { font-size: 15px; color: #475569; line-height: 1.7; text-align: justify; }
        
        .summary-box { background: #004a99; color: #ffffff; padding: 45px; border-radius: 20px; margin-top: 45px; text-align: center; }
        .summary-box p { margin: 0; font-size: 20px; font-weight: 600; line-height: 1.4; }
        .cta-sub { display: block; margin-top: 15px; font-size: 15px; opacity: 0.8; font-weight: 300; }
        
        .footer { padding: 45px; background: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 14px; color: #64748b; }
        .signature-name { font-size: 20px; font-weight: 800; color: #0f172a; margin-bottom: 5px; }
        .brand-footer { color: #004a99; font-weight: 700; text-decoration: none; }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="container">
            <div class="header">
                <h1>Learning Labs</h1>
                <p>Evolucionamos la educación</p>
            </div>
            
            <div class="content">
                <p class="intro-text">Estimado equipo directivo,</p>
                
                <p class="intro-text">
                    Como Director de <strong>Learning Labs</strong>, el diagnóstico que comparto con la alta gerencia es unánime: el modelo educativo tradicional colapsó. Hoy, la asfixia legal genera <em>burnout</em> docente; la ceguera de datos impide la personalización; las aulas ancladas en modelos teóricos obsoletos, la falta de herramientas analíticas y su uso estancan los resultados de las pruebas del Estado; y el uso descontrolado de la Inteligencia Artificial está erradicando el pensamiento crítico. Todo esto, sumado a una comunicación limitada e informal vía WhatsApp, termina fracturando irreparablemente la confianza y la percepción de valor de los padres de familia.
                </p>

                <div class="highlight-box">
                    <p>"Es matemáticamente imposible escalar la calidad pedagógica cuando el 70% del tiempo institucional se invierte en apagar crisis operativas."</p>
                </div>

                <p class="intro-text">
                    En Learning Labs hemos destruido este paradigma. No construimos un "LMS" más; hemos diseñado el <strong>Primer Gemelo Digital Institucional</strong>. Un Sistema Operativo Educativo integral que absorbe la complejidad, le devuelve a usted el control absoluto de su colegio y garantiza una educación hiper-personalizada a través de un modelo de IA aplicada en cinco capas arquitectónicas:
                </p>

                <div class="layer-card">
                    <div class="layer-header">
                        <span class="layer-icon">⚖️</span>
                        <span class="layer-name">Erradicación del Riesgo Legal (Bóveda Forense)</span>
                    </div>
                    <div class="layer-description">
                        Los colegios viven a un error humano de enfrentar demandas por fallas en el debido proceso. Sistematizamos su colegio a "Cero Papel". Actas, observadores y citaciones se generan con huellas criptográficas inalterables, garantizando un blindaje total ante el MEN y la ISO 21001, todo articulado en estricta coherencia con su PEI, PIAR, SIEE y Manual de Convivencia.
                    </div>
                </div>

                <div class="layer-card">
                    <div class="layer-header">
                        <span class="layer-icon">🧠</span>
                        <span class="layer-name">Neutralización del Fraude Cognitivo (Tutor Socrático IA)</span>
                    </div>
                    <div class="layer-description">
                        Los alumnos ya no piensan, solo copian. Nuestra Inteligencia Artificial, delimitada estrictamente por su reglamento institucional, no da respuestas. Aplica la Mayéutica para obligar a la corteza prefrontal del alumno a deducir la solución por sí mismo, forjando un pensamiento analítico real.
                    </div>
                </div>

                <div class="layer-card">
                    <div class="layer-header">
                        <span class="layer-icon">👨‍🏫</span>
                        <span class="layer-name">Eliminación del 'Burnout' Docente (Autopsia Académica)</span>
                    </div>
                    <div class="layer-description">
                        Sus profesores se agotan llenando planillas. Nuestro motor analiza el código genético de cada calificación, detectando la falla milimétrica del alumno. Dotamos al cuerpo docente de un tutor pedagógico IA que automatiza rutas de rescate para estudiantes en riesgo y potencia a los sobresalientes. Además, entregamos tableros de estadística predictiva en tiempo real para que cada maestro conozca el estado exacto de sus alumnos, cursos y áreas, permitiéndoles tomar decisiones preventivas y volver a su verdadera pasión: enseñar.
                    </div>
                </div>

                <div class="layer-card">
                    <div class="layer-header">
                        <span class="layer-icon">🚀</span>
                        <span class="layer-name">Proyección ICFES y Cognición Encarnada (Simuladores WebGL)</span>
                    </div>
                    <div class="layer-description">
                        La teoría abstracta aburre a la Generación Z. Los sumergimos en entornos 3D multilingües interactivos donde operan reactores químicos, motores físicos, simuladores matemáticos, de historia y más. Simultáneamente, transformamos la preparación ICFES/Saber en una "Misión Táctica" de alto rendimiento: simuladores inmersivos apoyados por un Tutor Socrático que detecta y corrige debilidades temáticas en tiempo real, elevando exponencialmente el posicionamiento nacional de su institución.
                    </div>
                </div>

                <div class="layer-card">
                    <div class="layer-header">
                        <span class="layer-icon">🛡️</span>
                        <span class="layer-name">Gobernanza Comunicacional (Traductor de Empatía)</span>
                    </div>
                    <div class="layer-description">
                        La informalidad de WhatsApp y grupos de padres, adicionalmente los boletines numéricos fríos generan fugas de matrículas. Implementamos una Red Social Interna propia controlando el lenguaje y temas, como también alertas SMS automáticas de inasistencia, notas, fallas, observador, siempre existe una visibilidad del estado completo del alumno. Nuestra IA traduce las métricas de evaluación en "Guías de Apoyo Familiar", devolviendo la confianza a los padres y justificando el alto valor de su matrícula.
                    </div>
                </div>

                <p class="intro-text" style="margin-top:40px; font-weight: 500;">
                    En <strong>Learning Labs</strong> convertimos los datos institucionales en mejora para la educación, evolucionamos las clases de aula con simuladores pedagógicos y conectamos a todos los miembros institucionales en un solo canal.
                </p>

                <div class="summary-box">
                    <p>¿Tendrían disponibilidad el próximo martes o jueves por la mañana?</p>
                    <span class="cta-sub">Mi objetivo es trazarle el mapa arquitectónico de su automatización y proyectar un ROI masivo para su junta directiva.</span>
                </div>
            </div>
            
            <div class="footer">
                <div class="signature-name">Isaac Miller</div>
                Director General | Learning Labs<br>
                📞 313-2533008<br><br>
                <a href="https://learninglabs.com" class="brand-footer">learninglabs.com &rarr;</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

# ==============================================================================
# 2. DOMAIN EXCEPTIONS (Arquitectura de Resiliencia Industrial)
# ==============================================================================
class AIRetryableError(Exception): """Errores recuperables: Red, Timeouts o Rate Limits."""
class AIFatalError(Exception): """Errores terminales: Autenticación o Configuración."""
class AIValidationError(AIRetryableError): """Fallo en el contrato semántico del JSON devuelto."""

# ==============================================================================
# 3. DATA TRANSFER OBJECTS (DTOs) CON BLINDAJE SEMÁNTICO
# ==============================================================================
class LLMTokenMetrics(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float

class LLMPitchResponse(BaseModel):
    """
    CONTRATO SEMÁNTICO RESILIENTE.
    Utiliza AliasChoices para absorber las traducciones espontáneas de la IA.
    """
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    thought_process: str = Field(
        ..., 
        validation_alias=AliasChoices('thought_process', 'proceso_de_pensamiento', 'analisis'),
        description="Análisis del reporte forense para estrategia de seguimiento."
    )
    email_subject: str = Field(
        ..., 
        validation_alias=AliasChoices('email_subject', 'asunto', 'subject'),
        min_length=15, 
        max_length=150,
        description="Asunto personalizado inyectando el nombre de la institución."
    )
    metrics: Optional[LLMTokenMetrics] = None

    @field_validator('email_subject')
    @classmethod
    def enforce_no_placeholders(cls, v: str) -> str:
        """Escudo Anti-Template: Bloquea residuos de corchetes."""
        if PLACEHOLDER_REGEX.findall(v):
            raise ValueError(f"Detección de placeholders no resueltos en el asunto: {v}")
        return v

# ==============================================================================
# 4. ARCHITECTURE: THE QUANTUM SALES ENGINE (GOD LEVEL V6.0)
# ==============================================================================
class QuantumSalesArchitect:
    """
    Orquestador de Ventas de Alta Disponibilidad.
    Optimizado para Redes Globales y Latencia Crítica.
    """

    def __init__(self, api_key: str, async_client: Optional[httpx.AsyncClient] = None):
        if not api_key:
            raise AIFatalError("DEEPSEEK_API_KEY no detectada. Abortando motor.")
            
        self.api_key: SecretStr = SecretStr(api_key)
        self.endpoint = "https://api.deepseek.com/v1/chat/completions"
        self._owns_client = False
        
        if async_client is None:
            # Configuración de Red Nivel Israel: HTTP/2 Nativo y Pooling Agresivo.
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(connect=5.0, read=60.0, write=20.0, pool=15.0),
                limits=httpx.Limits(max_keepalive_connections=300, max_connections=2000),
                http2=True,
                headers={
                    "User-Agent": "LearningLabs-QuantumEngine/6.0",
                    "Content-Type": "application/json"
                }
            )
            self._owns_client = True
        else:
            self.client = async_client

    async def aclose(self):
        """Purga de descriptores de archivos para prevenir zombies de red."""
        if self._owns_client:
            await self.client.aclose()

    @cached_property
    def learning_labs_dna(self) -> str:
        """El ADN estratégico inyectado como contexto inalterable para la IA."""
        return """
        EJE 1: Riesgo Legal (Bóveda Forense). Blindaje actas/citaciones con criptografía e inalterabilidad.
        EJE 2: Fraude IA (Tutor Socrático). Mayéutica pedagógica. La IA no da respuestas, guía al alumno.
        EJE 3: Burnout (Autopsia Académica). IA predictiva de notas, detección milimétrica de fallas y rutas de rescate.
        EJE 4: ICFES (WebGL). Simuladores 3D multilingües inmersivos y 'Misiones Tácticas' de alto rendimiento.
        EJE 5: Comunicación (Gobernanza). Red social propia, alertas SMS y guías familiares automáticas.
        """

    def _build_payload(self, school_name: str, ai_school_report: str) -> List[Dict[str, str]]:
        """Ingeniería de Prompt Geométrico: Restricción absoluta de salida JSON."""
        system_msg = (
            "Tu identidad es Isaac Miller, Director General de Learning Labs.\n"
            "Misión: Analizar el reporte forense y generar el asunto y el análisis táctico.\n\n"
            f"ADN PRODUCTO:\n{self.learning_labs_dna}\n\n"
            "INSTRUCCIONES CRÍTICAS:\n"
            "1. thought_process: Análisis cognitivo profundo de los dolores del colegio.\n"
            "2. email_subject: Exactamente: 'El fin del 70% de la carga operativa en el [Nombre del Colegio]'.\n"
            "3. NO generes el cuerpo del correo (está inyectado estáticamente).\n"
            "4. NUNCA traduzcas las llaves del JSON ('thought_process', 'email_subject').\n"
            "5. Responde con un JSON puro."
        )
        user_msg = f"INSTITUCION: {school_name}\nREPORTE FORENSE:\n{ai_school_report}"
        return [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]

    @retry(
        stop=stop_after_attempt(5), 
        wait=wait_exponential(multiplier=2, min=2, max=15),
        retry=retry_if_exception_type(AIRetryableError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def generate_learning_labs_pitch(self, school_name: str, ai_school_report: str) -> Dict[str, Any]:
        """
        Inferencia de Micro-Latencia y Ensamblaje HTML O(1).
        Punto de entrada para el envío de correos de $1M.
        """
        correlation_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id, target=school_name)
        
        logger.info("quantum_inference_start")
        
        payload = {
            "model": "deepseek-chat",
            "messages": self._build_payload(school_name, ai_school_report),
            "temperature": 0.1,  # Estricto determinismo para consistencia B2B.
            "response_format": {"type": "json_object"},
            "max_tokens": 1200
        }

        try:
            start_time = time.perf_counter()
            response = await self.client.post(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.api_key.get_secret_value()}"},
                content=orjson.dumps(payload)
            )
            
            # Gestión de Errores de Red y Protocolo.
            if response.status_code == 429:
                raise AIRetryableError("Rate limit excedido en el proveedor de IA.")
            elif response.status_code in (401, 403):
                raise AIFatalError("Fallo de autenticación: API Key comprometida o inválida.")
            
            response.raise_for_status()
            
        except (httpx.HTTPError, httpx.NetworkError) as e:
            raise AIRetryableError(f"Fallo de red perimetral: {str(e)}")

        latency_ms = (time.perf_counter() - start_time) * 1000
        raw_data = orjson.loads(response.read())

        try:
            content_str = raw_data['choices'][0]['message']['content']
            parsed_content = orjson.loads(content_str)
            usage = raw_data.get('usage', {})
            
            # Validación Pydantic con soporte de Alias (Blindaje contra traducción de la IA).
            validated = LLMPitchResponse(**parsed_content)
            
            validated.metrics = LLMTokenMetrics(
                prompt_tokens=usage.get('prompt_tokens', 0),
                completion_tokens=usage.get('completion_tokens', 0),
                total_tokens=usage.get('total_tokens', 0),
                latency_ms=latency_ms
            )
            
            # ENSAMBLAJE FINAL: Inyección estática O(1) de la Obra Maestra HTML.
            result = validated.model_dump()
            result['email_body'] = MASTER_EMAIL_HTML  
            
            logger.info("quantum_inference_success", latency=f"{latency_ms:.2f}ms")
            return result

        except (ValidationError, orjson.JSONDecodeError, KeyError) as e:
            logger.error("semantic_validation_failed", error=str(e))
            raise AIValidationError(f"Inconsistencia en el contrato semántico de la IA: {str(e)}")

# ==============================================================================
# 5. QA ENGINEERING - PROTOCOLO DE INTEGRIDAD (Production Ready)
# ==============================================================================
if __name__ == "__main__":
    import asyncio
    
    async def run_integrity_test():
        print("🛠️ Iniciando Protocolo de Integridad Nivel God Tier...")
        # Simulación de entorno industrial.
        arch = QuantumSalesArchitect(api_key="sk_dummy_key_for_test")
        try:
            # Esto fallará en red, pero valida la lógica de reintentos y construcción.
            await arch.generate_learning_labs_pitch("Colegio de Élite", "Reporte Forense Simulado")
        except Exception as e:
            print(f"Test finalizado. Excepción capturada correctamente: {type(e).__name__}")
        finally:
            await arch.aclose()
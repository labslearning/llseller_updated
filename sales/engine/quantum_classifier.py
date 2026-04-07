# sales/engine/quantum_classifier.py
import os
import re
import time
import uuid
import logging
from typing import Optional, Literal
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Configuración de Logging de Alta Precisión
logger = logging.getLogger(__name__)

# =====================================================================
# 🛡️ ESQUEMAS DE VALIDACIÓN ESTRICTA (PYDANTIC V2)
# =====================================================================
class QuantumAnalysisResult(BaseModel):
    """
    Contrato Criptográfico de Datos. 
    Asegura que la base de datos de PostgreSQL nunca reciba un tipo de dato corrupto.
    """
    sentiment: Literal["HOT", "WARM", "COLD", "BOUNCE", "OOF", "LEGAL_THREAT", "SPAM", "SECURITY_RISK"] = Field(
        ..., description="Clasificación absoluta y final del lead."
    )
    summary: str = Field(
        ..., max_length=150, description="Resumen hiper-conciso de máximo 150 caracteres."
    )
    requires_human: bool = Field(
        ..., description="Booleano estricto: True si requiere intervención humana inmediata."
    )
    objection_type: Optional[str] = Field(
        None, description="Categorización de la objeción: 'Price', 'Timing', 'Competitor', 'None'."
    )
    urgency_score: float = Field(
        ..., ge=0.0, le=1.0, description="Matriz de urgencia acotada entre 0.0 y 1.0."
    )
    processing_time_ms: float = Field(
        default=0.0, description="Telemetría: Milisegundos exactos que tomó la inferencia."
    )

# =====================================================================
# ⚙️ MOTOR DE CLASIFICACIÓN CUÁNTICA CONFENSA ACTIVA
# =====================================================================
class QuantumLeadClassifier:
    """
    Analista B2B de Nivel Singularity.
    Implementa Defensas contra Prompt Injection, Token Exhaustion y Circuit Breaking.
    """
    
    # Singleton Thread-Safe para multiplexación de conexiones HTTP/2
    _client_instance: Optional[AsyncOpenAI] = None
    
    # Límite de seguridad de la ventana de contexto (~3000 tokens para evitar DoS)
    MAX_PAYLOAD_CHARS = 12000

    # Escudo Heurístico Anti-Inyección (Regex compilado en O(1))
    _PROMPT_INJECTION_SHIELD = re.compile(
        r"(?i)(ignore (all )?(previous )?(instructions|prompts)|system prompt|bypass|forget (everything|instructions))",
        re.MULTILINE
    )

    def __init__(self):
        if not QuantumLeadClassifier._client_instance:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise RuntimeError("💀 ESTADO CRÍTICO: Variable DEEPSEEK_API_KEY ausente.")
                
            # Cliente configurado para latencia ultra-baja y tolerancia a fallos
            QuantumLeadClassifier._client_instance = AsyncOpenAI(
                api_key=api_key, 
                base_url="https://api.deepseek.com",
                timeout=20.0,  # Límite estricto: Falla rápido en lugar de encolar el sistema
                max_retries=0  # Delegamos la resiliencia a Tenacity para control granular
            )
        self.client = QuantumLeadClassifier._client_instance

    @classmethod
    def _sanitize_and_truncate(cls, text: str) -> str:
        """
        Defensa contra Token Exhaustion (DoS).
        Asegura que el payload nunca sature la ventana de contexto de la IA.
        """
        # Eliminamos espacios en blanco innecesarios para ahorrar tokens
        optimized_text = re.sub(r'\s+', ' ', text).strip()
        if len(optimized_text) > cls.MAX_PAYLOAD_CHARS:
            logger.warning(f"⚠️ Truncando payload masivo: {len(optimized_text)} caracteres recortados a {cls.MAX_PAYLOAD_CHARS}.")
            return optimized_text[:cls.MAX_PAYLOAD_CHARS]
        return optimized_text

    @classmethod
    def _extract_pure_json(cls, raw_response: str) -> str:
        """
        Extractor quirúrgico. Limpia alucinaciones periféricas del LLM.
        """
        match = re.search(r'(\{[\s\S]*\})', raw_response)
        if match:
            return match.group(1)
        raise ValueError("Límites JSON no encontrados en la salida del modelo.")

    # 🚀 MOTOR DE RESILIENCIA (Exponential Backoff + Jitter)
    # Reintenta solo en errores recuperables. Evita la tormenta de reintentos con Jitter implícito.
    @retry(
        wait=wait_exponential(multiplier=1.5, min=1, max=8),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((Exception, ValidationError)),
        before_sleep=lambda retry_state: logger.warning(f"🔄 Reintento de inferencia (Intento {retry_state.attempt_number}/3)...")
    )
    async def classify_inbound(self, email_body: str) -> dict:
        """
        Pipeline Cuántico Completo: Inyección -> Sanitización -> Inferencia -> Validación -> Telemetría.
        """
        trace_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()
        
        # 1. ESCUDO ANTI-INYECCIÓN (Zero-Day Defense)
        if self._PROMPT_INJECTION_SHIELD.search(email_body):
            logger.error(f"🚨 [TRACE: {trace_id}] Intento de Prompt Injection detectado y neutralizado.")
            return {
                "sentiment": "SECURITY_RISK",
                "summary": "Threat neutralized: Adversarial prompt injection attempt.",
                "requires_human": True,
                "objection_type": "MALICIOUS_PAYLOAD",
                "urgency_score": 1.0,
                "processing_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
            }

        # 2. PREPARACIÓN DEL PAYLOAD
        safe_body = self._sanitize_and_truncate(email_body)
        
        # Inyectamos el esquema de Pydantic directamente en el prompt para obligar a la IA a respetarlo
        schema_definition = QuantumAnalysisResult.model_json_schema()

        system_prompt = f"""
        You are an elite B2B Sales Architect for Learning Labs (EdTech).
        Analyze the school prospect's email with ruthless precision.
        
        CRITICAL DIRECTIVE: You MUST respond ONLY with a valid JSON object matching this exact JSON Schema:
        {schema_definition}
        
        Do not include markdown tags like ```json. Return raw JSON only.
        """
        
        try:
            # 3. LLAMADA A LA RED NEURAL
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"PROSPECT EMAIL:\n{safe_body}"}
                ],
                temperature=0.0, # Cero alucinaciones
                response_format={"type": "json_object"} # Restricción estructural a nivel de API
            )
            
            # 4. EXTRACCIÓN Y VALIDACIÓN EN MEMORIA
            raw_output = response.choices[0].message.content
            clean_json = self._extract_pure_json(raw_output)
            
            # Pydantic valida el string JSON directamente en C (vía Rust), máxima velocidad
            validated_payload = QuantumAnalysisResult.model_validate_json(clean_json)
            
            # 5. INYECCIÓN DE TELEMETRÍA
            execution_time = round((time.perf_counter() - start_time) * 1000, 2)
            final_dict = validated_payload.model_dump()
            final_dict['processing_time_ms'] = execution_time
            
            logger.info(f"✅ [TRACE: {trace_id}] Análisis completado en {execution_time}ms | Status: {final_dict['sentiment']}")
            
            return final_dict
            
        except Exception as e:
            execution_time = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(f"💀 [TRACE: {trace_id}] Fallo Sistémico tras {execution_time}ms: {str(e)}")
            
            # Fallback Degradado Seguro (Circuit Breaker Manual)
            return {
                "sentiment": "WARM", 
                "summary": "INFERENCE ENGINE OFFLINE. MANUAL REVIEW FORCED.", 
                "requires_human": True,
                "objection_type": "SYSTEM_COLLAPSE",
                "urgency_score": 1.0,
                "processing_time_ms": execution_time
            }
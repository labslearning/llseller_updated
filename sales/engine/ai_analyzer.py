"""
================================================================================
[TRANSCENDENT GOD TIER ARCHITECTURE: OMEGA QUANTUM LEVIATHAN CLASS ∞]
MODULE: COSMIC INTELLIGENCE ANALYZER - HYPER-AGGRESSIVE EXTRACTION ENGINE
VERSION: 99.9.9.9.9.OMEGA.FINAL
MODE: ZERO DATA LEFT BEHIND - ABSOLUTE EXTRACTION
STANDARD: SILICON VALLEY / TEL AVIV / WADI / SHANGHAI / TOKYO / DUBLIN / LONDON
================================================================================

Este analizador extrae ABSOLUTAMENTE TODA la información de una institución:
- Datos de contacto (emails, teléfonos, WhatsApp, redes sociales)
- LMS y tecnología (Moodle, Canvas, Phidias, Schoolnet, etc.)
- Certificaciones (IB, Cambridge, Oxford, ISO, EFQM, etc.)
- Programas académicos (STEM, Robótica, Programación, Idiomas)
- Infraestructura (laboratorios, instalaciones, transporte)
- Extracurriculares (deportes, artes, clubes, campamentos)
- Convenios (universidades, empresas, ONGs)
- Rendimiento (ICFES, premios, ranking)
- MISIÓN, VISIÓN, VALORES, FILOSOFÍA EDUCATIVA
- TODO lo que aparezca en la página web
"""

import os
import json
import logging
import asyncio
import hashlib
import time
import re
import uuid
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
import traceback

try:
    from openai import AsyncOpenAI, RateLimitError, APITimeoutError, APIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# =========================================================
# TELEMETRÍA
# =========================================================
logger = logging.getLogger("Sovereign.CosmicAnalyzer")

# =========================================================
# CONFIGURACIÓN GOD TIER OMEGA
# =========================================================
MAX_TEXT_LENGTH = 150000      # 150KB - Capturar TODO el texto (aumentado)
MAX_HTML_LENGTH = 75000       # 75KB de HTML (aumentado)
TEMPERATURE = 0.01            # Casi cero - máxima precisión
MAX_TOKENS = 15000            # Respuestas muy largas (aumentado)
CACHE_TTL = 86400 * 7         # 7 días de cache
RETRY_ATTEMPTS = 5
TIMEOUT = 120                 # 120 segundos para páginas grandes (aumentado)

# Pesos para cálculo de confianza
FIELD_WEIGHTS = {
    "emails": 3,
    "phones": 2,
    "mission": 5,
    "vision": 5,
    "values": 4,
    "levels_offered": 4,
    "lms_provider": 5,
    "has_robotics": 3,
    "icfes_score": 4,
    "executive_summary": 5,
    "social_media": 2,
    "address": 2,
    "foundation_year": 2,
    "pedagogical_model": 3,
    "languages_taught": 3,
    "university_agreements": 3,
    "sports": 2,
    "arts": 2,
}

# =========================================================
# CACHE PERSISTENTE (GOD TIER OMEGA)
# =========================================================
CACHE_DIR = Path("/tmp/cosmic_omega_cache")
CACHE_DIR.mkdir(exist_ok=True)
DB_PATH = CACHE_DIR / "cosmic_omega_cache.db"

class QuantumOmegaCache:
    """Cache persistente con SQLite y memoria RAM - GOD TIER OMEGA"""
    
    def __init__(self):
        self._memory_cache: Dict[str, Tuple[float, Any]] = {}
        self._hit_count = 0
        self._miss_count = 0
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS omega_cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    timestamp REAL,
                    ttl INTEGER,
                    access_count INTEGER DEFAULT 0,
                    last_access REAL DEFAULT 0
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_omega_timestamp ON omega_cache(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_omega_access ON omega_cache(access_count)")
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene del cache con seguimiento de hits/misses"""
        if key in self._memory_cache:
            timestamp, value = self._memory_cache[key]
            if time.time() - timestamp < CACHE_TTL:
                self._hit_count += 1
                return value
            del self._memory_cache[key]
        
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.execute(
                    "SELECT value, timestamp FROM omega_cache WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                if row:
                    value, timestamp = row
                    if time.time() - timestamp < CACHE_TTL:
                        self._memory_cache[key] = (timestamp, json.loads(value))
                        conn.execute(
                            "UPDATE omega_cache SET access_count = access_count + 1, last_access = ? WHERE key = ?",
                            (time.time(), key)
                        )
                        conn.commit()
                        self._hit_count += 1
                        return json.loads(value)
        except Exception as e:
            logger.debug(f"Omega cache read error: {e}")
        
        self._miss_count += 1
        return None
    
    def set(self, key: str, value: Any):
        try:
            serialized = json.dumps(value, ensure_ascii=False)
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO omega_cache (key, value, timestamp, ttl) VALUES (?, ?, ?, ?)",
                    (key, serialized, time.time(), CACHE_TTL)
                )
                conn.commit()
            self._memory_cache[key] = (time.time(), value)
            
            # Mantener memoria L1 limitada a 500 items (LRU)
            if len(self._memory_cache) > 500:
                oldest = min(self._memory_cache.keys(), key=lambda k: self._memory_cache[k][0])
                del self._memory_cache[oldest]
        except Exception as e:
            logger.debug(f"Omega cache write error: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        return {"hits": self._hit_count, "misses": self._miss_count}

OMEGA_CACHE = QuantumOmegaCache()


# =========================================================
# DATA STRUCTURE OMEGA COMPLETA - TODOS LOS CAMPOS
# =========================================================
@dataclass
class InstitutionProfile:
    """
    Perfil ultra-completo de la institución - NO DEJA NADA ATRÁS
    Esta es la clase principal que usa el sistema
    """
    
    # ========== IDENTIFICACIÓN ==========
    name: str = ""
    city: str = ""
    country: str = ""
    website: str = ""
    foundation_year: str = ""
    
    # ========== CONTACTOS (TODOS) ==========
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    whatsapp: List[str] = field(default_factory=list)
    social_media: Dict[str, str] = field(default_factory=dict)
    address: str = ""
    location_map: str = ""
    
    # ========== MISIÓN, VISIÓN, VALORES ==========
    mission: str = ""
    vision: str = ""
    values: List[str] = field(default_factory=list)
    educational_philosophy: str = ""
    institutional_horizon: str = ""
    educational_principles: List[str] = field(default_factory=list)
    
    # ========== ACADÉMICO ==========
    calendar: str = ""
    levels_offered: List[str] = field(default_factory=list)
    pedagogical_model: str = ""
    academic_emphasis: str = ""
    languages_taught: List[str] = field(default_factory=list)
    is_bilingual: bool = False
    is_trilingual: bool = False
    language_levels: Dict[str, str] = field(default_factory=dict)
    international_programs: List[str] = field(default_factory=list)
    
    # ========== TECNOLOGÍA (TODA) ==========
    lms_provider: str = ""
    lms_version: str = ""
    lms_confidence: float = 0.0
    tech_stack: Dict[str, Any] = field(default_factory=dict)
    digital_platforms: List[str] = field(default_factory=list)
    has_robotics: bool = False
    robotics_details: Dict[str, Any] = field(default_factory=dict)
    has_programming: bool = False
    programming_details: Dict[str, Any] = field(default_factory=dict)
    has_stem: bool = False
    stem_details: Dict[str, Any] = field(default_factory=dict)
    laboratories: List[str] = field(default_factory=list)
    classroom_tech: List[str] = field(default_factory=list)
    wifi_available: bool = False
    virtual_platform: str = ""
    
    # ========== CERTIFICACIONES (TODAS) ==========
    ib: Dict[str, Any] = field(default_factory=lambda: {
        "has_ib": False,
        "programs": [],
        "since": "",
        "coordinator": "",
        "authorization_date": ""
    })
    cambridge: Dict[str, Any] = field(default_factory=lambda: {
        "has_cambridge": False,
        "exams": [],
        "preparation_center": False,
        "since": "",
        "center_number": ""
    })
    oxford: Dict[str, Any] = field(default_factory=lambda: {"has_oxford": False})
    toefl: Dict[str, Any] = field(default_factory=lambda: {"has_toefl": False})
    ielts: Dict[str, Any] = field(default_factory=lambda: {"has_ielts": False})
    
    # Certificaciones de calidad
    iso_9001: bool = False
    iso_14001: bool = False
    efqm: bool = False
    great_place_to_study: bool = False
    other_certifications: List[str] = field(default_factory=list)
    
    # Certificaciones Colombianas
    men_resolution: str = ""
    icfes_registration: str = ""
    high_quality_accreditation: bool = False
    
    # ========== CONVENIOS Y ALIANZAS ==========
    university_agreements: List[str] = field(default_factory=list)
    corporate_agreements: List[str] = field(default_factory=list)
    international_agreements: List[str] = field(default_factory=list)
    ngo_agreements: List[str] = field(default_factory=list)
    government_programs: List[str] = field(default_factory=list)
    
    # ========== RENDIMIENTO ACADÉMICO ==========
    icfes_results: Dict[str, Any] = field(default_factory=dict)
    icfes_score: str = ""
    icfes_category: str = ""
    icfes_ranking: str = ""
    icfes_year: str = ""
    awards: List[str] = field(default_factory=list)
    recognitions: List[str] = field(default_factory=list)
    notable_alumni: List[str] = field(default_factory=list)
    university_admission_rate: str = ""
    top_universities: List[str] = field(default_factory=list)
    
    # ========== INFRAESTRUCTURA ==========
    campus_size: str = ""
    campus_locations: List[str] = field(default_factory=list)
    buildings: List[str] = field(default_factory=list)
    classrooms: int = 0
    laboratories_list: List[str] = field(default_factory=list)
    sports_facilities: List[str] = field(default_factory=list)
    library: Dict[str, Any] = field(default_factory=dict)
    dining: Dict[str, Any] = field(default_factory=dict)
    transportation: Dict[str, Any] = field(default_factory=dict)
    green_areas: bool = False
    accessibility: List[str] = field(default_factory=list)
    security_measures: List[str] = field(default_factory=list)
    
    # ========== EXTRACURRICULARES ==========
    sports: List[str] = field(default_factory=list)
    arts: List[str] = field(default_factory=list)
    clubs: List[str] = field(default_factory=list)
    camps: List[str] = field(default_factory=list)
    competitions: List[str] = field(default_factory=list)
    community_service: bool = False
    volunteer_programs: List[str] = field(default_factory=list)
    student_government: bool = False
    publications: List[str] = field(default_factory=list)
    
    # ========== PROYECTOS ESPECIALES ==========
    special_projects: List[str] = field(default_factory=list)
    innovation_initiatives: List[str] = field(default_factory=list)
    sustainability_programs: List[str] = field(default_factory=list)
    inclusion_programs: List[str] = field(default_factory=list)
    
    # ========== DATOS DEMOGRÁFICOS ==========
    student_count: int = 0
    teacher_count: int = 0
    student_teacher_ratio: str = ""
    average_class_size: int = 0
    
    # ========== ADMISIONES ==========
    admission_requirements: List[str] = field(default_factory=list)
    admission_process: str = ""
    scholarships: List[str] = field(default_factory=list)
    tuition_range: str = ""
    
    # ========== ANÁLISIS ESTRATÉGICO ==========
    swot_analysis: Dict[str, List[str]] = field(default_factory=dict)
    pain_points: List[str] = field(default_factory=list)
    sales_triggers: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    ideal_contact: str = ""
    recommended_approach: str = ""
    sales_priority: str = "Medium"
    estimated_revenue_potential: str = ""
    
    # ========== METADATOS ==========
    executive_summary: str = ""
    confidence_score: float = 0.0
    extraction_completeness: float = 0.0
    analysis_timestamp: float = 0.0
    trace_id: str = ""
    raw_text_length: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_markdown(self) -> str:
        """Genera reporte Markdown ultra-detallado - GOD TIER OMEGA"""
        
        md = f"""
# 🌌 COSMIC INTELLIGENCE REPORT - OMEGA EDITION
## {self.name}
### {self.city}, {self.country}

---

## 🎯 EXECUTIVE SUMMARY
{self.executive_summary or "No summary available."}

---

## 📞 CONTACT INFORMATION

### 📧 Emails
{self._format_list(self.emails)}

### 📞 Phones
{self._format_list(self.phones)}

### 💬 WhatsApp
{self._format_list(self.whatsapp)}

### 🌐 Social Media
{self._format_dict(self.social_media)}

### 📍 Address
{self.address or "Not specified"}

---

## 🏛️ INSTITUTIONAL IDENTITY

### Mission
{self.mission or "Not specified"}

### Vision
{self.vision or "Not specified"}

### Values
{self._format_list(self.values)}

### Educational Philosophy
{self.educational_philosophy or "Not specified"}

### Foundation Year
{self.foundation_year or "Not specified"}

---

## 📚 ACADEMIC PROFILE

| Field | Value |
|-------|-------|
| **Calendar** | {self.calendar or "Not specified"} |
| **Levels Offered** | {', '.join(self.levels_offered) or "Not specified"} |
| **Pedagogical Model** | {self.pedagogical_model or "Not specified"} |
| **Academic Emphasis** | {self.academic_emphasis or "Not specified"} |
| **Languages Taught** | {', '.join(self.languages_taught) or "Not specified"} |
| **Bilingual** | {'✅' if self.is_bilingual else '❌'} |
| **Trilingual** | {'✅' if self.is_trilingual else '❌'} |

---

## 🏆 CERTIFICATIONS & ACCREDITATIONS

### 🌍 International Certifications

| Certification | Status | Details |
|---------------|--------|---------|
| **IB** | {'✅' if self.ib.get('has_ib') else '❌'} | {', '.join(self.ib.get('programs', []))} |
| **Cambridge** | {'✅' if self.cambridge.get('has_cambridge') else '❌'} | {', '.join(self.cambridge.get('exams', []))} |
| **Oxford** | {'✅' if self.oxford.get('has_oxford') else '❌'} | - |
| **TOEFL** | {'✅' if self.toefl.get('has_toefl') else '❌'} | - |
| **IELTS** | {'✅' if self.ielts.get('has_ielts') else '❌'} | - |

### 🏅 Quality Certifications
- **ISO 9001**: {'✅' if self.iso_9001 else '❌'}
- **ISO 14001**: {'✅' if self.iso_14001 else '❌'}
- **EFQM**: {'✅' if self.efqm else '❌'}
- **Great Place to Study**: {'✅' if self.great_place_to_study else '❌'}

### 🇨🇴 Colombian Certifications
- **MEN Resolution**: {self.men_resolution or "Not specified"}
- **ICFES Registration**: {self.icfes_registration or "Not specified"}
- **High Quality Accreditation**: {'✅' if self.high_quality_accreditation else '❌'}

### Other Certifications
{self._format_list(self.other_certifications)}

---

## 🤖 TECHNOLOGY & INNOVATION

### LMS & Digital Platforms
| Aspect | Details |
|--------|---------|
| **LMS Provider** | {self.lms_provider or "Not detected"} |
| **LMS Version** | {self.lms_version or "Not specified"} |
| **Confidence** | {self.lms_confidence:.1%} |
| **Digital Platforms** | {', '.join(self.digital_platforms) or "None"} |

### Robotics
- **Status**: {'✅' if self.has_robotics else '❌'}
- **Details**: {json.dumps(self.robotics_details, indent=2, ensure_ascii=False) if self.robotics_details else "Not specified"}

### Programming
- **Status**: {'✅' if self.has_programming else '❌'}
- **Details**: {json.dumps(self.programming_details, indent=2, ensure_ascii=False) if self.programming_details else "Not specified"}

### STEM
- **Status**: {'✅' if self.has_stem else '❌'}
- **Details**: {json.dumps(self.stem_details, indent=2, ensure_ascii=False) if self.stem_details else "Not specified"}

### Laboratories
{self._format_list(self.laboratories)}

### Classroom Technology
{self._format_list(self.classroom_tech)}

### WiFi Available
{'✅' if self.wifi_available else '❌'}

### Virtual Platform
{self.virtual_platform or "Not specified"}

---

## 📊 PERFORMANCE & ACHIEVEMENTS

### ICFES Results
| Metric | Value |
|--------|-------|
| **Score** | {self.icfes_score or "Not available"} |
| **Category** | {self.icfes_category or "Not available"} |
| **Ranking** | {self.icfes_ranking or "Not available"} |
| **Year** | {self.icfes_year or "Not available"} |

### Awards & Recognitions
{self._format_list(self.awards)}

### Notable Alumni
{self._format_list(self.notable_alumni)}

### University Admission Rate
{self.university_admission_rate or "Not specified"}

### Top Universities (Graduation Destinations)
{self._format_list(self.top_universities)}

---

## 🏛️ INFRASTRUCTURE

| Aspect | Details |
|--------|---------|
| **Campus Size** | {self.campus_size or "Not specified"} |
| **Campus Locations** | {', '.join(self.campus_locations) or "Not specified"} |
| **Buildings** | {', '.join(self.buildings) or "Not specified"} |
| **Classrooms** | {self.classrooms or "Not specified"} |
| **Laboratories** | {', '.join(self.laboratories_list) or "Not specified"} |
| **Sports Facilities** | {', '.join(self.sports_facilities) or "Not specified"} |
| **Green Areas** | {'✅' if self.green_areas else '❌'} |

### Library
{self._format_dict(self.library)}

### Dining
{self._format_dict(self.dining)}

### Transportation
{self._format_dict(self.transportation)}

### Accessibility
{self._format_list(self.accessibility)}

### Security Measures
{self._format_list(self.security_measures)}

---

## 🎪 EXTRACURRICULAR ACTIVITIES

| Category | Activities |
|----------|------------|
| **Sports** | {', '.join(self.sports) or "None"} |
| **Arts** | {', '.join(self.arts) or "None"} |
| **Clubs** | {', '.join(self.clubs) or "None"} |
| **Camps** | {', '.join(self.camps) or "None"} |
| **Competitions** | {', '.join(self.competitions) or "None"} |

### Community Service
{'✅' if self.community_service else '❌'}

### Volunteer Programs
{self._format_list(self.volunteer_programs)}

### Student Government
{'✅' if self.student_government else '❌'}

### Publications
{self._format_list(self.publications)}

---

## 🤝 AGREEMENTS & PARTNERSHIPS

### University Agreements
{self._format_list(self.university_agreements)}

### Corporate Agreements
{self._format_list(self.corporate_agreements)}

### International Agreements
{self._format_list(self.international_agreements)}

### NGO Agreements
{self._format_list(self.ngo_agreements)}

### Government Programs
{self._format_list(self.government_programs)}

---

## 💼 SALES INTELLIGENCE

### 🔴 Pain Points
{self._format_list(self.pain_points)}

### 🟢 Sales Triggers
{self._format_list(self.sales_triggers)}

### 🚀 Opportunities
{self._format_list(self.opportunities)}

### ⚠️ Risks
{self._format_list(self.risks)}

### 👤 Ideal Contact
{self.ideal_contact or "Not specified"}

### 💰 Estimated Revenue Potential
{self.estimated_revenue_potential or "Not specified"}

### 🎯 Recommended Approach
{self.recommended_approach or "Not specified"}

### 📊 Sales Priority
{self.sales_priority}

---

## 📈 METADATA
- **Confidence Score**: {self.confidence_score:.1%}
- **Extraction Completeness**: {self.extraction_completeness:.1%}
- **Raw Text Length**: {self.raw_text_length:,} characters
- **Analysis Date**: {datetime.fromtimestamp(self.analysis_timestamp).strftime('%Y-%m-%d %H:%M:%S') if self.analysis_timestamp else "N/A"}
- **Trace ID**: {self.trace_id}

---

*Report generated by Cosmic Intelligence Engine OMEGA v99.9.9.9.9*
*Powered by DeepSeek AI - Hyper-Aggressive Extraction Mode*
"""
        return md
    
    def _format_list(self, items: List[str]) -> str:
        if not items:
            return "None"
        return "\n".join([f"- {item}" for item in items])
    
    def _format_dict(self, data: Dict) -> str:
        if not data:
            return "None"
        return "\n".join([f"- **{k}**: {v}" for k, v in data.items()])


# =========================================================
# EL ANALIZADOR OMEGA - CORAZÓN DEL SISTEMA
# =========================================================
class CosmicInstitutionAnalyzer:
    """
    Analizador ultra-agresivo que extrae ABSOLUTAMENTE TODO de la página web.
    Utiliza DeepSeek con un prompt masivo que busca cada detalle.
    Esta es la clase principal que usa el sistema.
    """
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.client = None
        self._stats = {
            "total_analyses": 0,
            "successful": 0,
            "failed": 0,
            "total_tokens": 0,
            "avg_latency_ms": 0
        }
        
        if self.api_key and OPENAI_AVAILABLE:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
                timeout=TIMEOUT,
                max_retries=0
            )
            logger.info("✅ Cosmic Analyzer Omega initialized with DeepSeek")
        else:
            logger.warning("⚠️ No API key found. AI analysis disabled.")
    
    def _generate_cache_key(self, name: str, city: str, country: str, text_hash: str) -> str:
        raw = f"omega_{name.lower()}_{city.lower()}_{country.lower()}_{text_hash}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]
    
    async def analyze(
        self,
        name: str,
        city: str,
        country: str,
        webpage_text: str,
        raw_html: Optional[str] = None,
        extracted_data: Optional[Dict] = None
    ) -> InstitutionProfile:
        """
        Análisis ultra-agresivo - Extrae TODO lo que encuentra
        """
        trace_id = uuid.uuid4().hex[:12]
        start_time = time.perf_counter()
        
        profile = InstitutionProfile(
            name=name,
            city=city,
            country=country,
            analysis_timestamp=time.time(),
            trace_id=trace_id,
            raw_text_length=len(webpage_text or "")
        )
        
        self._stats["total_analyses"] += 1
        
        logger.info(f"🌌 OMEGA [{trace_id}] Starting cosmic analysis: {name} | {city}, {country}")
        logger.info(f"📄 Text length: {len(webpage_text or 0):,} chars")
        
        if not self.client:
            profile.executive_summary = "⚠️ AI analysis unavailable (API not configured)"
            profile.confidence_score = 0.0
            self._stats["failed"] += 1
            return profile
        
        if not webpage_text or len(webpage_text.strip()) < 200:
            profile.executive_summary = f"⚠️ Insufficient text for analysis ({len(webpage_text or 0)} chars)"
            profile.confidence_score = 0.1
            self._stats["failed"] += 1
            return profile
        
        # Generar cache key
        text_hash = hashlib.md5(webpage_text[:10000].encode()).hexdigest()
        cache_key = self._generate_cache_key(name, city, country, text_hash)
        
        # Verificar cache
        cached = OMEGA_CACHE.get(cache_key)
        if cached:
            logger.info(f"⚡ OMEGA [{trace_id}] Cache HIT for {name}")
            for key, value in cached.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            elapsed = (time.perf_counter() - start_time) * 1000
            self._stats["avg_latency_ms"] = (self._stats["avg_latency_ms"] * (self._stats["total_analyses"] - 1) + elapsed) / self._stats["total_analyses"]
            self._stats["successful"] += 1
            return profile
        
        # Preparar texto
        safe_text = webpage_text[:MAX_TEXT_LENGTH]
        safe_html = (raw_html or "")[:MAX_HTML_LENGTH]
        
        # Construir prompt ultra-detallado
        prompt = self._build_omega_prompt(name, city, country, safe_text, safe_html, extracted_data)
        
        try:
            logger.info(f"🧠 OMEGA [{trace_id}] Sending request to DeepSeek API...")
            
            async def api_call():
                return await self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                )
            
            # Retry con backoff exponencial
            response = None
            last_error = None
            for attempt in range(RETRY_ATTEMPTS):
                try:
                    response = await api_call()
                    break
                except RateLimitError as e:
                    last_error = e
                    wait_time = (2 ** attempt) + (attempt * 0.5)
                    logger.warning(f"Rate limit (attempt {attempt + 1}/{RETRY_ATTEMPTS}), waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                except APITimeoutError as e:
                    last_error = e
                    wait_time = 1 ** attempt
                    logger.warning(f"Timeout (attempt {attempt + 1}/{RETRY_ATTEMPTS}), waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                except APIError as e:
                    last_error = e
                    wait_time = 2 ** attempt
                    logger.warning(f"API error (attempt {attempt + 1}/{RETRY_ATTEMPTS}): {e}")
                    await asyncio.sleep(wait_time)
                except Exception as e:
                    last_error = e
                    if attempt == RETRY_ATTEMPTS - 1:
                        raise
                    wait_time = 2 ** attempt
                    logger.warning(f"Error (attempt {attempt + 1}/{RETRY_ATTEMPTS}): {e}")
                    await asyncio.sleep(wait_time)
            
            if response is None:
                raise last_error or Exception("Max retries exceeded")
            
            raw_response = response.choices[0].message.content.strip()
            
            # Limpiar posibles marcadores de markdown
            if raw_response.startswith('```json'):
                raw_response = raw_response[7:]
            if raw_response.startswith('```'):
                raw_response = raw_response[3:]
            if raw_response.endswith('```'):
                raw_response = raw_response[:-3]
            
            data = json.loads(raw_response)
            
            # Registrar uso de tokens
            if hasattr(response, 'usage'):
                self._stats["total_tokens"] += response.usage.total_tokens
                logger.info(f"📊 OMEGA [{trace_id}] Tokens: {response.usage.total_tokens}")
            
            # Poblar el perfil
            self._populate_profile(profile, data)
            
            # Calcular métricas
            profile.confidence_score = self._calculate_confidence_weighted(data, len(webpage_text))
            profile.extraction_completeness = self._calculate_completeness_enhanced(data)
            
            # Guardar en cache
            OMEGA_CACHE.set(cache_key, profile.to_dict())
            
            elapsed = (time.perf_counter() - start_time) * 1000
            self._stats["avg_latency_ms"] = (self._stats["avg_latency_ms"] * (self._stats["total_analyses"] - 1) + elapsed) / self._stats["total_analyses"]
            self._stats["successful"] += 1
            
            logger.info(f"✅ OMEGA [{trace_id}] Analysis complete | Confidence: {profile.confidence_score:.1%} | Completeness: {profile.extraction_completeness:.1%} | {elapsed:.0f}ms")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ OMEGA [{trace_id}] JSON decode error: {e}")
            logger.error(f"Raw response (first 500 chars): {raw_response[:500]}")
            profile.executive_summary = f"❌ JSON decode error: {str(e)[:100]}"
            profile.confidence_score = 0.0
            self._stats["failed"] += 1
            
        except Exception as e:
            logger.error(f"❌ OMEGA [{trace_id}] Analysis failed: {e}")
            traceback.print_exc()
            profile.executive_summary = f"❌ Analysis failed: {str(e)[:200]}"
            profile.confidence_score = 0.0
            self._stats["failed"] += 1
        
        return profile
    
    def _get_system_prompt(self) -> str:
        return """You are the world's most advanced educational intelligence analyst - OMEGA EDITION.
Your mission: Extract EVERY piece of information from the institution's website.
Be OBSESSIVELY DETAILED. Leave NO stone unturned.
Output ONLY valid json. No markdown, no explanatory text.
Use empty arrays [] for missing data, empty strings "" for missing text.
Be AGGRESSIVE in extraction - if something is mentioned, capture it.
The JSON must be valid and complete."""

    def _build_omega_prompt(self, name: str, city: str, country: str, text: str, html: str, extracted: Dict) -> str:
        """Construye el prompt más detallado del mundo"""
        
        extracted_section = ""
        if extracted:
            extracted_section = f"""
PRE-VERIFIED DATA (ALREADY EXTRACTED - USE THIS):
- LMS: {extracted.get('lms_provider', 'Not detected')}
- Emails: {', '.join(extracted.get('emails', [])[:10])}
- Phones: {', '.join(extracted.get('phones', [])[:10])}
- WhatsApp: {', '.join(extracted.get('whatsapp', [])[:10])}
"""
        
        return f"""
TARGET INSTITUTION: {name}
LOCATION: {city}, {country}

{extracted_section}

==================== RAW WEBPAGE TEXT ====================
{text[:60000]}

==================== HTML CONTEXT (if available) ====================
{html[:20000]}

==================== YOUR MISSION ====================
Extract EVERY SINGLE piece of information from this institution's website.
Be OBSESSIVELY DETAILED. If something is mentioned, capture it.

=== WHAT TO EXTRACT (COMPLETE LIST - NO EXCEPTIONS) ===

1. CONTACT INFORMATION (ALL):
   - ALL email addresses (every single email, even if repeated)
   - ALL phone numbers (including extensions, PBX, etc.)
   - ALL WhatsApp numbers (including links to wa.me)
   - ALL social media links (Facebook, Instagram, LinkedIn, Twitter/X, YouTube, TikTok, WhatsApp, Telegram)
   - Complete physical address (street, number, city, postal code)
   - Google Maps links or coordinates

2. INSTITUTIONAL IDENTITY:
   - Mission statement (complete text, word for word)
   - Vision statement (complete text, word for word)
   - Values (list all values mentioned, including descriptions)
   - Educational philosophy (complete description)
   - Foundation year (exact year)
   - Institutional horizon (what they aspire to be)

3. ACADEMIC PROFILE:
   - Calendar type (A or B, traditional or international)
   - ALL levels offered (Preescolar, Jardín, Transición, Primaria, Bachillerato, Media, etc.)
   - Pedagogical model (Montessori, Constructivist, etc.)
   - Academic emphasis (STEM, Arts, Humanities, Sports, etc.)
   - Languages taught (Spanish, English, French, German, Portuguese, etc.)
   - Bilingual status (yes/no, which languages)
   - Trilingual status (yes/no, which languages)
   - Language levels (A1, A2, B1, B2, C1, C2)
   - International programs (Exchange, Study abroad, etc.)

4. TECHNOLOGY & LMS (COMPLETE):
   - LMS provider (Moodle, Canvas, Phidias, Schoolnet, Blackboard, Google Classroom, Microsoft Teams, etc.)
   - LMS version if visible
   - Other digital platforms used (Zoom, Meet, etc.)
   - Robotics program (details: type, platforms, competitions, achievements, grades)
   - Programming program (languages taught: Python, Java, Scratch, etc., frameworks, grade levels)
   - STEM program (details, projects, labs)
   - Laboratories (list all types: robotics, science, computers, physics, chemistry, biology, etc.)
   - Classroom technology (smartboards, tablets, laptops, projectors, etc.)
   - WiFi availability (yes/no, coverage)
   - Virtual learning platforms (Zoom, Meet, Teams, etc.)

5. CERTIFICATIONS & ACCREDITATIONS (ALL):
   - IB (International Baccalaureate): has_ib, programs (PYP/MYP/DP), since, coordinator, authorization date
   - Cambridge: has_cambridge, exams (PET, FCE, CAE, CPE, KET, YLE), preparation_center, since, center_number
   - Oxford: has_oxford
   - TOEFL: has_toefl, preparation_center
   - IELTS: has_ielts, preparation_center
   - ISO 9001 (Quality Management)
   - ISO 14001 (Environmental Management)
   - EFQM (Excellence Model)
   - Great Place to Study
   - MEN resolution number (Ministerio de Educación Nacional)
   - ICFES registration number
   - High Quality Accreditation (Acreditación de Alta Calidad)
   - Any other certifications (International, National, Local)

6. AGREEMENTS & PARTNERSHIPS:
   - University agreements (list all universities mentioned with details)
   - Corporate agreements (list all companies mentioned)
   - International agreements (list all countries/organizations)
   - NGO agreements (list all non-profits)
   - Government programs (list all government partnerships)

7. PERFORMANCE & RESULTS:
   - ICFES scores (numeric value, category A+/A/B/C/D, ranking, year, percentile)
   - Awards and recognitions (list all with years if available)
   - Notable alumni (list names and achievements)
   - University admission rate (percentage)
   - Top universities where graduates go (list of universities)

8. INFRASTRUCTURE:
   - Campus size (in square meters or acres)
   - Number of campuses/locations (list all addresses)
   - Buildings (list names/floors/purposes)
   - Number of classrooms
   - Laboratories (detailed list with purposes)
   - Sports facilities (fields, courts, gym, pool, track, etc.)
   - Library (size, number of volumes, digital access, study rooms)
   - Dining (cafeteria, restaurant, meal plans, dietary options)
   - Transportation (school bus, routes, schedules, coverage)
   - Green areas (parks, gardens, environmental spaces)
   - Accessibility features (ramps, elevators, adapted bathrooms)
   - Security measures (cameras, guards, access control)

9. EXTRACURRICULAR ACTIVITIES:
   - Sports (list all sports: soccer, basketball, volleyball, swimming, athletics, etc.)
   - Arts (music, theater, dance, painting, drawing, photography, etc.)
   - Clubs (robotics, chess, debate, science, math, reading, etc.)
   - Camps (summer, winter, language, sports, etc.)
   - Competitions participated/won (list with years and results)
   - Community service programs (details, hours required)
   - Volunteer opportunities (list of programs)
   - Student government (yes/no, structure)
   - Publications (newspaper, magazine, yearbook, blog)

10. DEMOGRAPHICS:
    - Number of students (total, by level if available)
    - Number of teachers (total, by level if available)
    - Student-teacher ratio
    - Average class size

11. ADMISSIONS:
    - Admission requirements (list all requirements)
    - Admission process (steps, timeline)
    - Scholarships available (list types: academic, sports, financial)
    - Tuition range (monthly or annual, in local currency)

12. SALES INTELLIGENCE (Strategic Analysis - CRITICAL):
    - Pain points: What problems does the institution face that our solution could solve?
      (Examples: outdated technology, lack of digital platform, high administrative workload, 
       poor student engagement, limited parent communication, etc.)
    - Sales triggers: What indicates they need our solution?
      (Examples: recent expansion, new campus, new technology director, 
       complaints about current system, looking for modernization, etc.)
    - Opportunities: Where can we add value?
      (Examples: digital transformation, new LMS implementation, robotics program expansion,
       teacher training, parent portal implementation, etc.)
    - Risks: What could prevent the sale?
      (Examples: budget constraints, recent investment in other technology, 
       resistant administration, long decision cycle, etc.)
    - Ideal contact person: Role/title of the best person to contact
    - Recommended sales approach: Strategy for approaching this institution
    - Estimated revenue potential: Low/Medium/High (based on size and needs)
    - Sales priority: High/Medium/Low (based on urgency and potential)

13. EXECUTIVE SUMMARY:
    - 2-3 sentence summary for the sales team (concise, actionable)

=== OUTPUT FORMAT (STRICT json - MUST BE VALID) ===
{
    "emails": ["email1", "email2"],
    "phones": ["phone1", "phone2"],
    "whatsapp": ["wa1", "wa2"],
    "social_media": {"facebook": "url", "instagram": "url", "linkedin": "url", "twitter": "url", "youtube": "url"},
    "address": "full address",
    "mission": "complete mission statement",
    "vision": "complete vision statement",
    "values": ["value1", "value2", "value3"],
    "educational_philosophy": "philosophy text",
    "foundation_year": "year",
    "calendar": "A or B",
    "levels_offered": ["Preescolar", "Primaria", "Bachillerato"],
    "pedagogical_model": "model name",
    "academic_emphasis": "emphasis description",
    "languages_taught": ["Español", "Inglés", "Francés"],
    "is_bilingual": true/false,
    "is_trilingual": true/false,
    "lms_provider": "Moodle/Canvas/Phidias/etc",
    "lms_version": "version if found",
    "lms_confidence": 0.0,
    "digital_platforms": ["Google Classroom", "Microsoft Teams"],
    "has_robotics": true/false,
    "robotics_details": {"type": "LEGO Education", "platforms": ["LEGO Mindstorms"], "competitions": ["FIRST LEGO League"], "achievements": ["Campeones 2023"]},
    "has_programming": true/false,
    "programming_details": {"languages": ["Python", "Scratch"], "frameworks": [], "grade_levels": ["5° a 11°"]},
    "has_stem": true/false,
    "stem_details": {"programs": ["STEM Lab", "Science Fair"], "projects": []},
    "laboratories": ["Robótica", "Ciencias", "Computación"],
    "classroom_tech": ["Smartboards", "Tablets"],
    "wifi_available": true/false,
    "virtual_platform": "Zoom/Meet/Teams",
    "ib": {"has_ib": true/false, "programs": ["PYP", "MYP", "DP"], "since": "2020", "coordinator": "", "authorization_date": ""},
    "cambridge": {"has_cambridge": true/false, "exams": ["PET", "FCE"], "preparation_center": true, "since": "", "center_number": "CO123"},
    "oxford": {"has_oxford": true/false},
    "toefl": {"has_toefl": true/false},
    "ielts": {"has_ielts": true/false},
    "iso_9001": true/false,
    "iso_14001": true/false,
    "efqm": true/false,
    "great_place_to_study": true/false,
    "other_certifications": ["cert1", "cert2"],
    "men_resolution": "resolution number",
    "icfes_registration": "registration number",
    "high_quality_accreditation": true/false,
    "university_agreements": ["Universidad de los Andes", "Universidad Javeriana"],
    "corporate_agreements": ["Microsoft", "LEGO Education"],
    "international_agreements": ["Exchange with Spain"],
    "ngo_agreements": [],
    "government_programs": [],
    "icfes_score": "78",
    "icfes_category": "A+",
    "icfes_ranking": "Top 10%",
    "icfes_year": "2023",
    "awards": ["Premio a la Excelencia"],
    "recognitions": [],
    "notable_alumni": ["Person Name"],
    "university_admission_rate": "85%",
    "top_universities": ["Universidad de los Andes"],
    "campus_size": "20,000 m²",
    "campus_locations": ["Sede principal", "Sede norte"],
    "buildings": [],
    "classrooms": 50,
    "laboratories_list": [],
    "sports_facilities": ["Cancha de fútbol", "Gimnasio", "Piscina"],
    "library": {"size": "5,000 volumes", "digital_access": true, "study_rooms": 5},
    "dining": {"has_cafeteria": true, "meal_plans": true, "options": []},
    "transportation": {"has_school_bus": true, "routes": ["Norte", "Sur"], "schedules": []},
    "green_areas": true,
    "accessibility": [],
    "security_measures": [],
    "sports": ["Fútbol", "Baloncesto", "Natación"],
    "arts": ["Música", "Teatro", "Danza"],
    "clubs": ["Ajedrez", "Robótica", "Debate"],
    "camps": ["Campamento de inglés", "Campamento de verano"],
    "competitions": ["FIRST LEGO League", "Olimpiadas de Matemáticas"],
    "community_service": true,
    "volunteer_programs": [],
    "student_government": true,
    "publications": [],
    "special_projects": [],
    "innovation_initiatives": [],
    "sustainability_programs": [],
    "inclusion_programs": [],
    "student_count": 1200,
    "teacher_count": 80,
    "student_teacher_ratio": "15:1",
    "average_class_size": 25,
    "admission_requirements": ["Entrevista", "Prueba de admisión"],
    "admission_process": "",
    "scholarships": ["Excelencia académica", "Becas deportivas"],
    "tuition_range": "$5,000,000 - $8,000,000 COP",
    "pain_points": ["Falta de plataforma digital unificada", "Sistemas obsoletos"],
    "sales_triggers": ["Expansión de campus", "Certificación IB reciente"],
    "opportunities": ["Migración a LMS moderno", "Implementación de robótica"],
    "risks": ["Presupuesto limitado", "Competencia local"],
    "ideal_contact": "Rector o Director de Tecnología",
    "recommended_approach": "Demostración técnica seguida de propuesta económica",
    "estimated_revenue_potential": "Alto",
    "sales_priority": "High",
    "executive_summary": "Resumen ejecutivo para el equipo de ventas"
}

EXTRACT EVERYTHING YOU FIND. BE THOROUGH. LEAVE NOTHING OUT. RESPOND WITH ONLY valid json.
"""

    def _populate_profile(self, profile: InstitutionProfile, data: Dict):
        """Pobla el perfil con los datos extraídos"""
        
        # Contactos
        profile.emails = data.get('emails', [])
        profile.phones = data.get('phones', [])
        profile.whatsapp = data.get('whatsapp', [])
        profile.social_media = data.get('social_media', {})
        profile.address = data.get('address', '')
        
        # Identidad
        profile.mission = data.get('mission', '')
        profile.vision = data.get('vision', '')
        profile.values = data.get('values', [])
        profile.educational_philosophy = data.get('educational_philosophy', '')
        profile.foundation_year = data.get('foundation_year', '')
        
        # Académico
        profile.calendar = data.get('calendar', '')
        profile.levels_offered = data.get('levels_offered', [])
        profile.pedagogical_model = data.get('pedagogical_model', '')
        profile.academic_emphasis = data.get('academic_emphasis', '')
        profile.languages_taught = data.get('languages_taught', [])
        profile.is_bilingual = data.get('is_bilingual', False)
        profile.is_trilingual = data.get('is_trilingual', False)
        
        # Tecnología
        profile.lms_provider = data.get('lms_provider', '')
        profile.lms_version = data.get('lms_version', '')
        profile.lms_confidence = data.get('lms_confidence', 0.0)
        profile.digital_platforms = data.get('digital_platforms', [])
        profile.has_robotics = data.get('has_robotics', False)
        profile.robotics_details = data.get('robotics_details', {})
        profile.has_programming = data.get('has_programming', False)
        profile.programming_details = data.get('programming_details', {})
        profile.has_stem = data.get('has_stem', False)
        profile.stem_details = data.get('stem_details', {})
        profile.laboratories = data.get('laboratories', [])
        profile.classroom_tech = data.get('classroom_tech', [])
        profile.wifi_available = data.get('wifi_available', False)
        profile.virtual_platform = data.get('virtual_platform', '')
        
        # Certificaciones
        profile.ib = data.get('ib', profile.ib)
        profile.cambridge = data.get('cambridge', profile.cambridge)
        profile.oxford = data.get('oxford', profile.oxford)
        profile.toefl = data.get('toefl', profile.toefl)
        profile.ielts = data.get('ielts', profile.ielts)
        profile.iso_9001 = data.get('iso_9001', False)
        profile.iso_14001 = data.get('iso_14001', False)
        profile.efqm = data.get('efqm', False)
        profile.great_place_to_study = data.get('great_place_to_study', False)
        profile.other_certifications = data.get('other_certifications', [])
        profile.men_resolution = data.get('men_resolution', '')
        profile.icfes_registration = data.get('icfes_registration', '')
        profile.high_quality_accreditation = data.get('high_quality_accreditation', False)
        
        # Convenios
        profile.university_agreements = data.get('university_agreements', [])
        profile.corporate_agreements = data.get('corporate_agreements', [])
        profile.international_agreements = data.get('international_agreements', [])
        profile.ngo_agreements = data.get('ngo_agreements', [])
        profile.government_programs = data.get('government_programs', [])
        
        # Rendimiento
        profile.icfes_score = data.get('icfes_score', '')
        profile.icfes_category = data.get('icfes_category', '')
        profile.icfes_ranking = data.get('icfes_ranking', '')
        profile.icfes_year = data.get('icfes_year', '')
        profile.awards = data.get('awards', [])
        profile.recognitions = data.get('recognitions', [])
        profile.notable_alumni = data.get('notable_alumni', [])
        profile.university_admission_rate = data.get('university_admission_rate', '')
        profile.top_universities = data.get('top_universities', [])
        
        # Infraestructura
        profile.campus_size = data.get('campus_size', '')
        profile.campus_locations = data.get('campus_locations', [])
        profile.buildings = data.get('buildings', [])
        profile.classrooms = data.get('classrooms', 0)
        profile.laboratories_list = data.get('laboratories_list', [])
        profile.sports_facilities = data.get('sports_facilities', [])
        profile.library = data.get('library', {})
        profile.dining = data.get('dining', {})
        profile.transportation = data.get('transportation', {})
        profile.green_areas = data.get('green_areas', False)
        profile.accessibility = data.get('accessibility', [])
        profile.security_measures = data.get('security_measures', [])
        
        # Extracurriculares
        profile.sports = data.get('sports', [])
        profile.arts = data.get('arts', [])
        profile.clubs = data.get('clubs', [])
        profile.camps = data.get('camps', [])
        profile.competitions = data.get('competitions', [])
        profile.community_service = data.get('community_service', False)
        profile.volunteer_programs = data.get('volunteer_programs', [])
        profile.student_government = data.get('student_government', False)
        profile.publications = data.get('publications', [])
        
        # Proyectos especiales
        profile.special_projects = data.get('special_projects', [])
        profile.innovation_initiatives = data.get('innovation_initiatives', [])
        profile.sustainability_programs = data.get('sustainability_programs', [])
        profile.inclusion_programs = data.get('inclusion_programs', [])
        
        # Demografía
        profile.student_count = data.get('student_count', 0)
        profile.teacher_count = data.get('teacher_count', 0)
        profile.student_teacher_ratio = data.get('student_teacher_ratio', '')
        profile.average_class_size = data.get('average_class_size', 0)
        
        # Admisiones
        profile.admission_requirements = data.get('admission_requirements', [])
        profile.admission_process = data.get('admission_process', '')
        profile.scholarships = data.get('scholarships', [])
        profile.tuition_range = data.get('tuition_range', '')
        
        # Inteligencia de ventas
        profile.pain_points = data.get('pain_points', [])
        profile.sales_triggers = data.get('sales_triggers', [])
        profile.opportunities = data.get('opportunities', [])
        profile.risks = data.get('risks', [])
        profile.ideal_contact = data.get('ideal_contact', '')
        profile.recommended_approach = data.get('recommended_approach', '')
        profile.estimated_revenue_potential = data.get('estimated_revenue_potential', '')
        profile.sales_priority = data.get('sales_priority', 'Medium')
        
        # Resumen ejecutivo
        profile.executive_summary = data.get('executive_summary', '')
    
    def _calculate_confidence_weighted(self, data: Dict, text_length: int) -> float:
        """Calcula la confianza del análisis con pesos por campo crítico"""
        if not data:
            return 0.0
        
        total_weight = 0
        filled_weight = 0
        
        def process_value(value, weight):
            nonlocal filled_weight
            if value:
                if isinstance(value, (list, dict)):
                    if value:
                        filled_weight += weight
                elif value not in (None, "", False):
                    filled_weight += weight
        
        for field, weight in FIELD_WEIGHTS.items():
            total_weight += weight
            value = data.get(field)
            if isinstance(value, dict):
                # Para diccionarios anidados, verificar si tiene algún valor
                has_value = any(v for v in value.values() if v)
                if has_value:
                    filled_weight += weight
            else:
                process_value(value, weight)
        
        # También contar campos adicionales importantes
        additional_fields = ["social_media", "address", "foundation_year", "pedagogical_model"]
        for field in additional_fields:
            if field not in FIELD_WEIGHTS:
                total_weight += 2
                if data.get(field):
                    filled_weight += 2
        
        field_score = filled_weight / max(total_weight, 1) if total_weight > 0 else 0
        text_factor = min(1.0, text_length / 15000)
        
        return (field_score * 0.7) + (text_factor * 0.3)
    
    def _calculate_completeness_enhanced(self, data: Dict) -> float:
        """Calcula la completitud de la extracción con campos críticos"""
        if not data:
            return 0.0
        
        critical_fields = [
            "emails", "phones", "mission", "vision", "values", "levels_offered",
            "lms_provider", "has_robotics", "icfes_score", "executive_summary",
            "social_media", "address", "foundation_year", "languages_taught"
        ]
        
        completed = 0
        for field in critical_fields:
            value = data.get(field)
            if value:
                if isinstance(value, list) and value:
                    completed += 1
                elif isinstance(value, dict) and any(v for v in value.values() if v):
                    completed += 1
                elif value not in (None, "", False):
                    completed += 1
        
        return completed / len(critical_fields)
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del analizador"""
        cache_stats = OMEGA_CACHE.get_stats()
        return {
            **self._stats,
            "cache_hits": cache_stats["hits"],
            "cache_misses": cache_stats["misses"],
            "success_rate": self._stats["successful"] / max(1, self._stats["total_analyses"])
        }
    
    def clear_cache(self):
        """Limpia la caché"""
        OMEGA_CACHE._memory_cache.clear()
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("DELETE FROM omega_cache")
                conn.commit()
        except Exception as e:
            logger.debug(f"Cache clear error: {e}")
        logger.info("🗑️ Omega cache cleared")


# =================================================================================
# EXPORT FUNCTIONS (MANTIENEN COMPATIBILIDAD CON EL SISTEMA EXISTENTE)
# =================================================================================
_analyzer = None

def get_analyzer() -> CosmicInstitutionAnalyzer:
    """Obtiene la instancia única del analizador"""
    global _analyzer
    if _analyzer is None:
        _analyzer = CosmicInstitutionAnalyzer()
    return _analyzer

async def analyze_institution(
    name: str,
    city: str,
    country: str,
    webpage_text: str,
    raw_html: Optional[str] = None,
    extracted_data: Optional[Dict] = None
) -> InstitutionProfile:
    """Analiza una institución de forma asíncrona"""
    analyzer = get_analyzer()
    return await analyzer.analyze(name, city, country, webpage_text, raw_html, extracted_data)

def analyze_institution_sync(
    name: str,
    city: str,
    country: str,
    webpage_text: str,
    raw_html: Optional[str] = None,
    extracted_data: Optional[Dict] = None
) -> InstitutionProfile:
    """Analiza una institución de forma síncrona (para uso en hilos)"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            analyze_institution(name, city, country, webpage_text, raw_html, extracted_data)
        )
    finally:
        loop.close()


# =================================================================================
# SELF-TEST
# =================================================================================
async def self_test():
    """Prueba automática del analizador"""
    logger.info("🧪 Running Omega self-test...")
    
    test_text = """
    Colegio Gimnasio Los Arrayanes
    Fundado en 1995
    Misión: Formar líderes integrales con excelencia académica y valores humanos.
    Visión: Ser reconocidos como la mejor institución educativa de la región para 2030.
    Valores: Respeto, Responsabilidad, Honestidad, Solidaridad.
    
    Ofrecemos educación desde preescolar hasta bachillerato.
    Calendario A (enero a noviembre).
    Somos un colegio bilingüe español-inglés con certificación Cambridge.
    Contamos con programa de robótica LEGO Education y participamos en FIRST LEGO League.
    En 2023 obtuvimos puntaje ICFES de 82 en categoría A+.
    
    Infraestructura: campus de 15,000 m² con laboratorios de ciencias, robótica y computación.
    Cancha de fútbol, gimnasio cubierto, piscina semiolímpica.
    Biblioteca con 8,000 volúmenes y acceso digital.
    Transporte escolar con 5 rutas.
    
    Extracurriculares: fútbol, baloncesto, natación, música, teatro, ajedrez, debate.
    Convenios con Universidad de los Andes y Universidad Javeriana.
    Convenios empresariales con Microsoft y LEGO Education.
    
    Contacto: info@losarrayanes.edu.co, 601-1234567, WhatsApp: 3131234567
    Facebook: /losarrayanes, Instagram: @losarrayanes
    """
    
    analyzer = get_analyzer()
    profile = await analyzer.analyze(
        name="Colegio Gimnasio Los Arrayanes",
        city="Bogotá",
        country="Colombia",
        webpage_text=test_text
    )
    
    print("\n" + "="*80)
    print("📊 OMEGA SELF-TEST RESULTS")
    print("="*80)
    print(f"Name: {profile.name}")
    print(f"Confidence: {profile.confidence_score:.1%}")
    print(f"Completeness: {profile.extraction_completeness:.1%}")
    print(f"Emails: {profile.emails}")
    print(f"Phones: {profile.phones}")
    print(f"WhatsApp: {profile.whatsapp}")
    print(f"Social Media: {profile.social_media}")
    print(f"Address: {profile.address}")
    print(f"Mission: {profile.mission[:100]}...")
    print(f"Vision: {profile.vision[:100]}...")
    print(f"Values: {profile.values}")
    print(f"Levels: {profile.levels_offered}")
    print(f"Calendar: {profile.calendar}")
    print(f"Bilingual: {profile.is_bilingual}")
    print(f"Languages: {profile.languages_taught}")
    print(f"LMS: {profile.lms_provider}")
    print(f"Robotics: {profile.has_robotics}")
    print(f"Robotics Details: {profile.robotics_details}")
    print(f"ICFES: {profile.icfes_score} - {profile.icfes_category}")
    print(f"Sports: {profile.sports}")
    print(f"Arts: {profile.arts}")
    print(f"Clubs: {profile.clubs}")
    print(f"University Agreements: {profile.university_agreements}")
    print(f"Corporate Agreements: {profile.corporate_agreements}")
    print(f"Campus Size: {profile.campus_size}")
    print(f"Sports Facilities: {profile.sports_facilities}")
    print(f"Pain Points: {profile.pain_points}")
    print(f"Sales Triggers: {profile.sales_triggers}")
    print(f"Opportunities: {profile.opportunities}")
    print(f"Ideal Contact: {profile.ideal_contact}")
    print(f"Executive Summary: {profile.executive_summary}")
    print("\n" + "="*80)
    print("✅ Omega self-test completed")
    print("="*80)
    
    # Mostrar estadísticas
    stats = analyzer.get_stats()
    print(f"\n📊 Statistics: {stats}")

if __name__ == "__main__":
    asyncio.run(self_test())
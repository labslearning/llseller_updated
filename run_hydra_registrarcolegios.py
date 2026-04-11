import os
import time
import json
import django
from django.utils import timezone

# ==========================================
# 0. INICIALIZAR ENTORNO DJANGO ALTO RENDIMIENTO
# ==========================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from django.db import transaction
from sales.models import Contact, Institution, TechProfile, DeepForensicProfile

# Si tienes la tarea de email, descomenta la siguiente línea
# from sales.tasks import execute_step_1_email

# 1. FORZADO DE IDENTIDAD ABSOLUTA
settings.DEFAULT_FROM_EMAIL = "Miller Ospina | Learning Labs <efectomiller@gmail.com>"

def despliegue_hydra_swarm_omega():
    print("\n" + "═"*75)
    print("🌌 [GOD TIER] INICIANDO PROTOCOLO HYDRA SWARM OMEGA (5 OBJETIVOS)")
    print("═"*75 + "\n")

    # 2. CARGA DE PAYLOADS ESTRATÉGICOS (MÁXIMA DENSIDAD DE DATOS)
    objetivos = [
        {
            "email": "profealejandromyfgla@gmail.com",
            "colegio": "Academia MyFGLA de Ciencias (TEST)",
            "domain": "myfgla.edu.co",
            "phone": "+57 300 111 2222",
            "city": "Bogotá",
            "lms": "Moodle",
            "score": 85,
            "analisis": "Institución enfocada en ciencias aplicadas. Necesitan laboratorios virtuales de química y física para sus estudiantes de secundaria.",
            "ia_data": {
                "is_bilingual": True, "has_stem": True, "has_robotics": False,
                "certifications": {"cambridge": {"has_cambridge": True}},
                "performance": {"icfes": {"score": 350, "category": "A+"}}
            }
        },
        {
            "email": "analyticshydra@gmail.com",
            "colegio": "Hydra Data Analytics Institute (TEST)",
            "domain": "hydradata.edu.co",
            "phone": "+57 310 333 4444",
            "city": "Medellín",
            "lms": "Canvas",
            "score": 92,
            "analisis": "Colegio altamente digitalizado. Buscan integrar un LMS avanzado que les proporcione métricas predictivas sobre el rendimiento estudiantil.",
            "ia_data": {
                "is_bilingual": True, "is_trilingual": True, "has_stem": True, "has_programming": True,
                "certifications": {"ib": {"has_ib": True}},
                "performance": {"icfes": {"score": 380, "category": "A+"}}
            }
        },
        {
            "email": "hydraschool5@gmail.com",
            "colegio": "Hydra Preparatory - Campus 5 (TEST)",
            "domain": "hydrap5.edu.co",
            "phone": "+57 315 555 6666",
            "city": "Chía",
            "lms": "Phidias",
            "score": 78,
            "analisis": "Sede en expansión. Requieren simuladores de gestión y plataformas escalables para estandarizar la educación técnica.",
            "ia_data": {
                "is_bilingual": True, "has_robotics": True,
                "performance": {"icfes": {"score": 320, "category": "A"}}
            }
        },
        {
            "email": "hydraschoolcolombia@gmail.com",
            "colegio": "Colegio Bilingüe Hydra Colombia (TEST)",
            "domain": "hydracol.edu.co",
            "phone": "+57 320 777 8888",
            "city": "Cali",
            "lms": "Schoolnet",
            "score": 88,
            "analisis": "Enfoque principal en bilingüismo tecnológico e inglés inmersivo. Potencial enorme para simuladores de élite en inglés.",
            "ia_data": {
                "is_bilingual": True, "is_trilingual": True,
                "certifications": {"cambridge": {"has_cambridge": True}, "ib": {"has_ib": True}},
                "performance": {"icfes": {"score": 365, "category": "A+"}}
            }
        },
        {
            "email": "efectomiller@gmail.com",
            "colegio": "Instituto de Innovación Efecto Miller (TEST)",
            "domain": "efectomiller.edu.co",
            "phone": "+57 300 999 0000",
            "city": "Chía",
            "lms": "Cibercolegios",
            "score": 95,
            "analisis": "Centro de alto rendimiento educativo. Líderes en robótica y programación competitiva.",
            "ia_data": {
                "has_robotics": True, "has_stem": True, "has_programming": True,
                "performance": {"icfes": {"score": 390, "category": "A+"}}
            }
        }
    ]

    for i, obj in enumerate(objetivos, 1):
        print(f"🎯 INYECTANDO CLÚSTER [{i}/5]: {obj['colegio']}")
        try:
            # Transacción atómica: Si algo falla, se revierte todo para este colegio
            with transaction.atomic():
                
                # A. CONSTRUCCIÓN DE LA BASE DE DATOS (NÚCLEO)
                # Inyectamos el email directamente en la institución para el Dashboard
                inst, created = Institution.objects.update_or_create(
                    name=obj['colegio'],
                    defaults={
                        'website': f"https://www.{obj['domain']}",
                        'email': obj['email'], # <--- AQUÍ ESTÁ LA MAGIA PARA EL DASHBOARD
                        'phone': obj['phone'],
                        'city': obj['city'],
                        'country': "Colombia",
                        'institution_type': "school",
                        'is_private': True,
                        'lead_score': obj['score'],
                        'last_scored_at': timezone.now(),
                        'processing_status': 'ENRICHED'
                    }
                )

                # B. PERFIL TECNOLÓGICO (Enciende los badges de LMS en el Radar)
                TechProfile.objects.update_or_create(
                    institution=inst,
                    defaults={
                        'has_lms': True,
                        'lms_provider': obj['lms']
                    }
                )

                # C. PERFIL FORENSE DE INTELIGENCIA (Enciende los badges Cósmicos: IB, STEM, etc.)
                DeepForensicProfile.objects.update_or_create(
                    institution=inst,
                    defaults={
                        'ai_comprehensive_report': f"# Reporte Cósmico: {obj['colegio']}\n\n**Resumen:**\n{obj['analisis']}\n\n**Vectores de Ataque:**\n- Necesidad de Simuladores WebGL.\n- Optimización de carga operativa docente.",
                        'ai_structured_data': obj['ia_data'], # JSON inyectado directamente
                        'is_bilingual': obj['ia_data'].get('is_bilingual', False),
                        'is_trilingual': obj['ia_data'].get('is_trilingual', False),
                        'has_ib_cert': obj['ia_data'].get('certifications', {}).get('ib', {}).get('has_ib', False),
                        'has_cambridge_cert': obj['ia_data'].get('certifications', {}).get('cambridge', {}).get('has_cambridge', False)
                    }
                )

                # D. REGISTRO DEL CONTACTO (Para que la IA tenga a quién responderle)
                Contact.objects.update_or_create(
                    institution=inst,
                    email=obj['email'],
                    defaults={
                        'name': "Director Académico",
                        'phone': obj['phone'],
                        'is_decision_maker': True
                    }
                )

            print(f"   [+] 🟢 Vault Sincronizado. Datos enriquecidos.")

            # E. IGNICIÓN (Descomentar en producción para enviar correo real)
            # print("   [+] 🚀 DeepSeek analizando... Disparando misil!")
            # resultado = execute_step_1_email(contact_id=inst.contacts.first().id)
            # print(f"   [+] ✅ IMPACTO CONFIRMADO: {resultado}")
            
            time.sleep(0.5) # Pausa mínima para no saturar la consola

        except Exception as e:
            print(f"   [!] ❌ FALLO CRÍTICO en Clúster {i}: {str(e)}")

    print("\n" + "═"*75)
    print("✨ OPERACIÓN HYDRA SWARM COMPLETADA. REVISA EL GLOBAL PIPELINE COSMIC.")
    print("═"*75 + "\n")

if __name__ == "__main__":
    despliegue_hydra_swarm_omega()

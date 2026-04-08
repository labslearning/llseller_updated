import os
import time
import django

# ==========================================
# 0. INICIALIZAR ENTORNO DJANGO
# ==========================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from sales.models import Contact, Institution, OutreachSequence, DeepForensicProfile
from sales.tasks import execute_step_1_email

# 1. FORZADO DE IDENTIDAD ABSOLUTA
settings.DEFAULT_FROM_EMAIL = "Learning Labs | LMS avanzado && Simuladores educativos de elite <efectomiller@gmail.com>"

def despliegue_hydra_swarm():
    print("🔥 INICIANDO PROTOCOLO HYDRA SWARM (5 OBJETIVOS)...")
    print("=" * 65)

    # 2. DEFINICIÓN DE OBJETIVOS ESTRATÉGICOS
    objetivos = [
        {
            "email": "profealejandromyfgla@gmail.com",
            "colegio": "Academia MyFGLA de Ciencias (TEST)",
            "analisis": "Institución enfocada en ciencias aplicadas. Necesitan laboratorios virtuales de química y física para sus estudiantes de secundaria."
        },
        {
            "email": "analyticshydra@gmail.com",
            "colegio": "Hydra Data Analytics Institute (TEST)",
            "analisis": "Colegio altamente digitalizado. Buscan integrar un LMS avanzado que les proporcione métricas predictivas sobre el rendimiento estudiantil."
        },
        {
            "email": "hydraschool5@gmail.com",
            "colegio": "Hydra Preparatory - Campus 5 (TEST)",
            "analisis": "Sede en expansión. Requieren simuladores de gestión y plataformas escalables para estandarizar la educación técnica."
        },
        {
            "email": "hydraschoolcolombia@gmail.com",
            "colegio": "Colegio Bilingüe Hydra Colombia (TEST)",
            "analisis": "Enfoque principal en bilingüismo tecnológico e inglés inmersivo. Potencial enorme para simuladores de élite en inglés."
        },
        {
            "email": "efectomiller@gmail.com",
            "colegio": "Instituto de Innovación Efecto Miller (TEST)",
            "analisis": "Centro de alto rendimiento educativo. Líderes en robótica y programación competitiva."
        }
    ]

    # 3. AUTO-DESCUBRIMIENTO DEL PERFIL FORENSE
    campos_perfil = [f.name for f in DeepForensicProfile._meta.get_fields() 
                     if not f.is_relation and f.name != 'id' and 'date' not in f.name]

    for i, obj in enumerate(objetivos, 1):
        print(f"\n🎯 FIJANDO OBJETIVO [{i}/5]: {obj['email']}")
        try:
            # A. Construir Infraestructura
            inst, _ = Institution.objects.update_or_create(
                name=obj['colegio'],
                defaults={'website': f"https://test-{i}.learninglabs.ai"}
            )

            # B. Inyectar Combustible IA
            datos_perfil = {}
            if campos_perfil:
                datos_perfil[campos_perfil[0]] = obj['analisis']
            
            DeepForensicProfile.objects.update_or_create(
                institution=inst,
                defaults=datos_perfil
            )

            # C. Registrar Contacto
            contacto, _ = Contact.objects.update_or_create(
                email=obj['email'],
                defaults={'institution': inst}
            )

            # D. Limpiar Telemetría Previa
            OutreachSequence.objects.filter(contact=contacto).delete()
            print(f"   [+] Base de datos sincronizada para {obj['colegio']}")

            # E. IGNICIÓN
            print("   [+] 🚀 DeepSeek analizando... Disparando misil!")
            resultado = execute_step_1_email(contact_id=contacto.id)
            print(f"   [+] ✅ IMPACTO CONFIRMADO: {resultado}")
            
            # Pausa táctica
            time.sleep(2)

        except Exception as e:
            print(f"   [!] ❌ ERROR en Objetivo {i}: {str(e)}")

    print("\n" + "=" * 65)
    print("✨ OPERACIÓN HYDRA SWARM COMPLETADA CON ÉXITO.")

if __name__ == "__main__":
    despliegue_hydra_swarm()

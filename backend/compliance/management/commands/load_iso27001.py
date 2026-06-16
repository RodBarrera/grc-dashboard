"""
Comando de gestión: carga el catálogo de controles de ISO/IEC 27001:2022 (Anexo A).

Uso:
    python manage.py load_iso27001

Es idempotente: usa get_or_create, así que ejecutarlo varias veces no duplica
datos. Los títulos corresponden a los 93 controles del Anexo A organizados en
los 4 temas de la versión 2022.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from compliance.models import Framework, Control

# (código, título, dominio)
CONTROLS = [
    # --- A.5 Controles organizacionales (37) ---
    ("A.5.1", "Políticas de seguridad de la información", "Organizacional"),
    ("A.5.2", "Roles y responsabilidades de seguridad de la información", "Organizacional"),
    ("A.5.3", "Segregación de funciones", "Organizacional"),
    ("A.5.4", "Responsabilidades de la dirección", "Organizacional"),
    ("A.5.5", "Contacto con autoridades", "Organizacional"),
    ("A.5.6", "Contacto con grupos de interés especial", "Organizacional"),
    ("A.5.7", "Inteligencia de amenazas", "Organizacional"),
    ("A.5.8", "Seguridad de la información en la gestión de proyectos", "Organizacional"),
    ("A.5.9", "Inventario de información y otros activos asociados", "Organizacional"),
    ("A.5.10", "Uso aceptable de la información y otros activos asociados", "Organizacional"),
    ("A.5.11", "Devolución de activos", "Organizacional"),
    ("A.5.12", "Clasificación de la información", "Organizacional"),
    ("A.5.13", "Etiquetado de la información", "Organizacional"),
    ("A.5.14", "Transferencia de información", "Organizacional"),
    ("A.5.15", "Control de acceso", "Organizacional"),
    ("A.5.16", "Gestión de identidades", "Organizacional"),
    ("A.5.17", "Información de autenticación", "Organizacional"),
    ("A.5.18", "Derechos de acceso", "Organizacional"),
    ("A.5.19", "Seguridad de la información en las relaciones con proveedores", "Organizacional"),
    ("A.5.20", "Seguridad de la información en los acuerdos con proveedores", "Organizacional"),
    ("A.5.21", "Gestión de la seguridad en la cadena de suministro de TIC", "Organizacional"),
    ("A.5.22", "Seguimiento, revisión y gestión de cambios de servicios de proveedores", "Organizacional"),
    ("A.5.23", "Seguridad de la información para el uso de servicios en la nube", "Organizacional"),
    ("A.5.24", "Planificación y preparación de la gestión de incidentes", "Organizacional"),
    ("A.5.25", "Evaluación y decisión sobre eventos de seguridad de la información", "Organizacional"),
    ("A.5.26", "Respuesta a incidentes de seguridad de la información", "Organizacional"),
    ("A.5.27", "Aprendizaje de los incidentes de seguridad de la información", "Organizacional"),
    ("A.5.28", "Recopilación de evidencias", "Organizacional"),
    ("A.5.29", "Seguridad de la información durante la disrupción", "Organizacional"),
    ("A.5.30", "Preparación de las TIC para la continuidad del negocio", "Organizacional"),
    ("A.5.31", "Requisitos legales, estatutarios, reglamentarios y contractuales", "Organizacional"),
    ("A.5.32", "Derechos de propiedad intelectual", "Organizacional"),
    ("A.5.33", "Protección de registros", "Organizacional"),
    ("A.5.34", "Privacidad y protección de datos personales (PII)", "Organizacional"),
    ("A.5.35", "Revisión independiente de la seguridad de la información", "Organizacional"),
    ("A.5.36", "Cumplimiento de políticas, reglas y normas de seguridad", "Organizacional"),
    ("A.5.37", "Procedimientos operativos documentados", "Organizacional"),
    # --- A.6 Controles de personas (8) ---
    ("A.6.1", "Investigación de antecedentes", "Personas"),
    ("A.6.2", "Términos y condiciones de empleo", "Personas"),
    ("A.6.3", "Concienciación, educación y formación en seguridad", "Personas"),
    ("A.6.4", "Proceso disciplinario", "Personas"),
    ("A.6.5", "Responsabilidades tras el cese o cambio de empleo", "Personas"),
    ("A.6.6", "Acuerdos de confidencialidad o no divulgación", "Personas"),
    ("A.6.7", "Trabajo remoto", "Personas"),
    ("A.6.8", "Notificación de eventos de seguridad de la información", "Personas"),
    # --- A.7 Controles físicos (14) ---
    ("A.7.1", "Perímetros de seguridad física", "Físico"),
    ("A.7.2", "Entrada física", "Físico"),
    ("A.7.3", "Seguridad de oficinas, salas e instalaciones", "Físico"),
    ("A.7.4", "Monitoreo de seguridad física", "Físico"),
    ("A.7.5", "Protección contra amenazas físicas y ambientales", "Físico"),
    ("A.7.6", "Trabajo en áreas seguras", "Físico"),
    ("A.7.7", "Escritorio limpio y pantalla limpia", "Físico"),
    ("A.7.8", "Ubicación y protección de equipos", "Físico"),
    ("A.7.9", "Seguridad de activos fuera de las instalaciones", "Físico"),
    ("A.7.10", "Soportes de almacenamiento", "Físico"),
    ("A.7.11", "Servicios de suministro", "Físico"),
    ("A.7.12", "Seguridad del cableado", "Físico"),
    ("A.7.13", "Mantenimiento de equipos", "Físico"),
    ("A.7.14", "Eliminación segura o reutilización de equipos", "Físico"),
    # --- A.8 Controles tecnológicos (34) ---
    ("A.8.1", "Dispositivos de usuario final", "Tecnológico"),
    ("A.8.2", "Derechos de acceso privilegiado", "Tecnológico"),
    ("A.8.3", "Restricción del acceso a la información", "Tecnológico"),
    ("A.8.4", "Acceso al código fuente", "Tecnológico"),
    ("A.8.5", "Autenticación segura", "Tecnológico"),
    ("A.8.6", "Gestión de la capacidad", "Tecnológico"),
    ("A.8.7", "Protección contra malware", "Tecnológico"),
    ("A.8.8", "Gestión de vulnerabilidades técnicas", "Tecnológico"),
    ("A.8.9", "Gestión de la configuración", "Tecnológico"),
    ("A.8.10", "Eliminación de información", "Tecnológico"),
    ("A.8.11", "Enmascaramiento de datos", "Tecnológico"),
    ("A.8.12", "Prevención de fuga de datos", "Tecnológico"),
    ("A.8.13", "Respaldo de información", "Tecnológico"),
    ("A.8.14", "Redundancia de instalaciones de procesamiento de información", "Tecnológico"),
    ("A.8.15", "Registro de eventos (logging)", "Tecnológico"),
    ("A.8.16", "Actividades de monitoreo", "Tecnológico"),
    ("A.8.17", "Sincronización de relojes", "Tecnológico"),
    ("A.8.18", "Uso de programas utilitarios privilegiados", "Tecnológico"),
    ("A.8.19", "Instalación de software en sistemas operativos", "Tecnológico"),
    ("A.8.20", "Seguridad de redes", "Tecnológico"),
    ("A.8.21", "Seguridad de los servicios de red", "Tecnológico"),
    ("A.8.22", "Segregación de redes", "Tecnológico"),
    ("A.8.23", "Filtrado web", "Tecnológico"),
    ("A.8.24", "Uso de criptografía", "Tecnológico"),
    ("A.8.25", "Ciclo de vida de desarrollo seguro", "Tecnológico"),
    ("A.8.26", "Requisitos de seguridad de aplicaciones", "Tecnológico"),
    ("A.8.27", "Principios de arquitectura e ingeniería de sistemas seguros", "Tecnológico"),
    ("A.8.28", "Codificación segura", "Tecnológico"),
    ("A.8.29", "Pruebas de seguridad en desarrollo y aceptación", "Tecnológico"),
    ("A.8.30", "Desarrollo externalizado", "Tecnológico"),
    ("A.8.31", "Separación de entornos de desarrollo, prueba y producción", "Tecnológico"),
    ("A.8.32", "Gestión de cambios", "Tecnológico"),
    ("A.8.33", "Información de prueba", "Tecnológico"),
    ("A.8.34", "Protección de sistemas durante pruebas de auditoría", "Tecnológico"),
]


class Command(BaseCommand):
    help = "Carga los 93 controles del Anexo A de ISO/IEC 27001:2022."

    @transaction.atomic
    def handle(self, *args, **options):
        framework, created = Framework.objects.get_or_create(
            name="ISO/IEC 27001",
            version="2022",
            defaults={
                "description": "Sistema de gestión de seguridad de la información. "
                "Controles del Anexo A (93 controles, 4 temas)."
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Marco creado: {framework}"))
        else:
            self.stdout.write(f"Marco ya existente: {framework}")

        nuevos = 0
        for code, title, domain in CONTROLS:
            _, was_created = Control.objects.get_or_create(
                framework=framework,
                code=code,
                defaults={"title": title, "domain": domain},
            )
            if was_created:
                nuevos += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Controles cargados: {nuevos} nuevos "
                f"(total en el marco: {framework.controls.count()})."
            )
        )

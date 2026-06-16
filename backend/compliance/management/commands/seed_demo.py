"""
Comando de gestión: siembra datos de demostración para el dashboard.

Uso:
    python manage.py seed_demo

Crea activos, riesgos y evaluaciones de control con una distribución realista
para que el panel se vea completo. Es idempotente: no duplica activos ni riesgos
por nombre, y solo evalúa controles que aún no tengan evaluación.

Requiere que el catálogo ISO ya esté cargado (python manage.py load_iso27001).
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from compliance.models import Control, ControlAssessment, Asset, Risk

# Por dominio: (implementados, parciales). El resto queda "no implementado".
DOMAIN_SPREAD = {
    "Organizacional": (24, 6),
    "Personas": (6, 1),
    "Físico": (9, 2),
    "Tecnológico": (20, 6),
}

ASSETS = [
    ("Servidor web de producción", "server", "high", "Equipo de Infraestructura"),
    ("Base de datos de clientes", "database", "critical", "DBA"),
    ("Aplicación de facturación", "application", "high", "Desarrollo"),
    ("Firewall perimetral", "network", "critical", "Redes"),
    ("Estaciones de trabajo RRHH", "endpoint", "medium", "Soporte TI"),
    ("Repositorio de código fuente", "data", "high", "Desarrollo"),
]

# (título, criticidad_activo_idx, probabilidad, impacto, estado, tratamiento)
RISKS = [
    ("Acceso no autorizado por credenciales débiles", 0, 4, 4, "open",
     "Implementar MFA y política de contraseñas robustas."),
    ("Fuga de datos de clientes por inyección SQL", 1, 4, 5, "open",
     "Revisión de código y consultas parametrizadas."),
    ("Interrupción del servicio por ransomware", 4, 3, 5, "mitigating",
     "Respaldo offline y segmentación de red."),
    ("Configuración insegura del firewall", 3, 3, 4, "open",
     "Auditoría de reglas y endurecimiento."),
    ("Pérdida de información por falta de respaldos", 2, 2, 4, "mitigating",
     "Política de respaldos automatizados."),
    ("Exposición de secretos en el repositorio", 5, 3, 3, "open",
     "Escaneo de secretos en el pipeline CI/CD."),
    ("Phishing dirigido al personal", 4, 3, 2, "accepted",
     "Campañas de concienciación periódicas."),
]


class Command(BaseCommand):
    help = "Siembra datos de demostración (activos, riesgos, evaluaciones)."

    def handle(self, *args, **options):
        if not Control.objects.exists():
            self.stderr.write(
                "No hay controles. Ejecute primero: python manage.py load_iso27001"
            )
            return

        User = get_user_model()
        evaluador = User.objects.filter(is_superuser=True).first() or User.objects.first()

        # --- Activos ---
        activos = []
        for name, atype, crit, owner in ASSETS:
            a, _ = Asset.objects.get_or_create(
                name=name,
                defaults={"asset_type": atype, "criticality": crit, "owner": owner},
            )
            activos.append(a)
        self.stdout.write(self.style.SUCCESS(f"Activos: {len(activos)}"))

        # --- Riesgos ---
        nuevos_riesgos = 0
        for title, idx, likelihood, impact, status, treatment in RISKS:
            _, created = Risk.objects.get_or_create(
                title=title,
                defaults={
                    "asset": activos[idx] if idx < len(activos) else None,
                    "likelihood": likelihood,
                    "impact": impact,
                    "status": status,
                    "treatment": treatment,
                },
            )
            nuevos_riesgos += int(created)
        self.stdout.write(self.style.SUCCESS(f"Riesgos nuevos: {nuevos_riesgos}"))

        # --- Evaluaciones de control ---
        evaluados = 0
        for domain, (n_impl, n_partial) in DOMAIN_SPREAD.items():
            controls = list(
                Control.objects.filter(domain=domain).order_by("code")
            )
            for i, control in enumerate(controls):
                if ControlAssessment.objects.filter(control=control).exists():
                    continue
                if i < n_impl:
                    estado = ControlAssessment.Status.IMPLEMENTED
                elif i < n_impl + n_partial:
                    estado = ControlAssessment.Status.PARTIAL
                else:
                    estado = ControlAssessment.Status.NOT_IMPLEMENTED
                ControlAssessment.objects.create(
                    control=control, status=estado, assessed_by=evaluador
                )
                evaluados += 1
        self.stdout.write(self.style.SUCCESS(f"Controles evaluados: {evaluados}"))
        self.stdout.write("Datos de demostración listos.")

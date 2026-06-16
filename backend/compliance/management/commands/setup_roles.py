"""
Comando de gestión: crea los grupos de roles de la aplicación.

Uso:
    python manage.py setup_roles

Crea los grupos "Auditor" y "Responsable" si no existen. Es idempotente.
La asignación de usuarios a cada grupo se hace desde el admin de Django.
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

ROLES = ["Auditor", "Responsable"]


class Command(BaseCommand):
    help = "Crea los grupos de roles (Auditor, Responsable)."

    def handle(self, *args, **options):
        for name in ROLES:
            group, created = Group.objects.get_or_create(name=name)
            estado = "creado" if created else "ya existía"
            self.stdout.write(self.style.SUCCESS(f"Grupo '{name}': {estado}."))
        self.stdout.write(
            "Asigne usuarios a estos grupos desde /admin/ → Usuarios."
        )

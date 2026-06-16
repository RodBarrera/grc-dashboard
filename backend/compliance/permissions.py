"""
Permisos basados en roles (RBAC) para la API.

Roles (grupos de Django):
- Auditor: lectura total + crear/editar evaluaciones de control.
- Responsable: gestión (CRUD) de activos, riesgos y evaluaciones.
- Superusuario: acceso total, único que puede borrar.

Cada ViewSet declara qué grupos pueden escribir mediante el atributo
`write_groups`. El borrado queda reservado al superusuario salvo que la vista
lo amplíe con `delete_groups`.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


def in_groups(user, names):
    """True si el usuario pertenece a alguno de los grupos indicados."""
    if not names:
        return False
    return user.groups.filter(name__in=names).exists()


class RolePermission(BasePermission):
    """Permiso configurable por rol, leído desde atributos del ViewSet."""

    message = "No tiene permisos suficientes para esta acción según su rol."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        # El superusuario siempre puede.
        if user.is_superuser:
            return True

        # Lectura: cualquier usuario autenticado.
        if request.method in SAFE_METHODS:
            return True

        # Borrado: solo grupos explícitamente autorizados (por defecto, ninguno).
        if request.method == "DELETE":
            return in_groups(user, getattr(view, "delete_groups", []))

        # Escritura (POST, PUT, PATCH): grupos declarados en la vista.
        return in_groups(user, getattr(view, "write_groups", []))

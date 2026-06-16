"""
Vistas para el dashboard y la autenticación del frontend.

- dashboard_stats: agrega las métricas que consume el panel (cumplimiento,
  desglose por dominio, estado de controles y resumen de riesgos).
- login: autentica usuario/contraseña y devuelve un token + sus roles.
"""

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Control, ControlAssessment, Asset, Risk


def _latest_status_by_control():
    """Devuelve {control_id: estado} con la evaluación más reciente de cada control."""
    latest = {}
    qs = ControlAssessment.objects.order_by("control_id", "-assessed_at")
    for a in qs:
        # Como viene ordenado, el primero de cada control es el más reciente.
        if a.control_id not in latest:
            latest[a.control_id] = a.status
    return latest


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Métricas agregadas para el panel de control."""
    controls = list(Control.objects.all())
    total = len(controls)
    latest = _latest_status_by_control()

    implemented = sum(
        1 for c in controls if latest.get(c.id) == ControlAssessment.Status.IMPLEMENTED
    )
    partial = sum(
        1 for c in controls if latest.get(c.id) == ControlAssessment.Status.PARTIAL
    )
    not_applicable = sum(
        1 for c in controls if latest.get(c.id) == ControlAssessment.Status.NOT_APPLICABLE
    )
    # Controles aplicables = total menos los marcados como "no aplica".
    applicable = total - not_applicable
    compliance = round((implemented / applicable) * 100, 1) if applicable else 0.0

    # Desglose por dominio.
    domains = {}
    for c in controls:
        d = domains.setdefault(
            c.domain or "Sin dominio", {"total": 0, "implemented": 0}
        )
        d["total"] += 1
        if latest.get(c.id) == ControlAssessment.Status.IMPLEMENTED:
            d["implemented"] += 1
    by_domain = [
        {
            "domain": name,
            "total": v["total"],
            "implemented": v["implemented"],
            "percentage": round((v["implemented"] / v["total"]) * 100, 1)
            if v["total"]
            else 0.0,
        }
        for name, v in sorted(domains.items())
    ]

    # Resumen de riesgos por clasificación.
    risks = list(Risk.objects.all())
    risk_ratings = {"Crítico": 0, "Alto": 0, "Medio": 0, "Bajo": 0}
    for r in risks:
        risk_ratings[r.risk_rating] = risk_ratings.get(r.risk_rating, 0) + 1
    open_risks = sum(1 for r in risks if r.status == Risk.Status.OPEN)

    return Response(
        {
            "compliance_percentage": compliance,
            "controls": {
                "total": total,
                "implemented": implemented,
                "partial": partial,
                "not_applicable": not_applicable,
                "not_assessed": total - len(latest),
            },
            "by_domain": by_domain,
            "assets": {
                "total": Asset.objects.count(),
            },
            "risks": {
                "total": len(risks),
                "open": open_risks,
                "by_rating": risk_ratings,
            },
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Autentica y devuelve un token de acceso junto con los roles del usuario."""
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {"detail": "Credenciales inválidas."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            "token": token.key,
            "username": user.username,
            "is_superuser": user.is_superuser,
            "roles": list(user.groups.values_list("name", flat=True)),
        }
    )

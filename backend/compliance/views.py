"""Vistas de la API — ViewSets de DRF con control de acceso por roles."""

from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Framework, Control, Asset, ControlAssessment, Risk
from .permissions import RolePermission
from .serializers import (
    FrameworkSerializer,
    ControlSerializer,
    AssetSerializer,
    ControlAssessmentSerializer,
    RiskSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Endpoint de salud para verificar que el backend responde."""
    return Response({"status": "ok", "service": "grc-dashboard-api"})


class FrameworkViewSet(viewsets.ModelViewSet):
    """Catálogo de marcos: lectura para todos, escritura solo superusuario."""

    queryset = Framework.objects.all()
    serializer_class = FrameworkSerializer
    permission_classes = [RolePermission]
    write_groups = []  # solo superusuario
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "version"]
    ordering_fields = ["name", "created_at"]


class ControlViewSet(viewsets.ModelViewSet):
    """Catálogo de controles: lectura para todos, escritura solo superusuario."""

    queryset = Control.objects.select_related("framework").all()
    serializer_class = ControlSerializer
    permission_classes = [RolePermission]
    write_groups = []  # solo superusuario
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code", "title", "domain"]
    ordering_fields = ["code", "domain"]


class AssetViewSet(viewsets.ModelViewSet):
    """Activos: gestionados por el rol Responsable."""

    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [RolePermission]
    write_groups = ["Responsable"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "owner"]
    ordering_fields = ["name", "criticality", "created_at"]


class ControlAssessmentViewSet(viewsets.ModelViewSet):
    """Evaluaciones de control: creadas por Auditor o Responsable."""

    queryset = ControlAssessment.objects.select_related("control").all()
    serializer_class = ControlAssessmentSerializer
    permission_classes = [RolePermission]
    write_groups = ["Auditor", "Responsable"]

    def perform_create(self, serializer):
        # Registra automáticamente quién hizo la evaluación.
        serializer.save(assessed_by=self.request.user)


class RiskViewSet(viewsets.ModelViewSet):
    """Riesgos: gestionados por el rol Responsable."""

    queryset = Risk.objects.select_related("asset").all()
    serializer_class = RiskSerializer
    permission_classes = [RolePermission]
    write_groups = ["Responsable"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "likelihood", "impact"]

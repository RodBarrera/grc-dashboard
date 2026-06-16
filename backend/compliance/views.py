"""Vistas de la API — ViewSets de DRF para cada entidad + endpoint de salud."""

from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Framework, Control, Asset, ControlAssessment, Risk
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
    queryset = Framework.objects.all()
    serializer_class = FrameworkSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "version"]
    ordering_fields = ["name", "created_at"]


class ControlViewSet(viewsets.ModelViewSet):
    queryset = Control.objects.select_related("framework").all()
    serializer_class = ControlSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code", "title", "domain"]
    ordering_fields = ["code", "domain"]


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "owner"]
    ordering_fields = ["name", "criticality", "created_at"]


class ControlAssessmentViewSet(viewsets.ModelViewSet):
    queryset = ControlAssessment.objects.select_related("control").all()
    serializer_class = ControlAssessmentSerializer

    def perform_create(self, serializer):
        # Registra automáticamente quién hizo la evaluación.
        serializer.save(assessed_by=self.request.user)


class RiskViewSet(viewsets.ModelViewSet):
    queryset = Risk.objects.select_related("asset").all()
    serializer_class = RiskSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "likelihood", "impact"]

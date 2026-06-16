"""Rutas de la app compliance — router de DRF + endpoint de salud."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"frameworks", views.FrameworkViewSet)
router.register(r"controls", views.ControlViewSet)
router.register(r"assets", views.AssetViewSet)
router.register(r"assessments", views.ControlAssessmentViewSet)
router.register(r"risks", views.RiskViewSet)

urlpatterns = [
    path("health/", views.health, name="health"),
    path("", include(router.urls)),
]

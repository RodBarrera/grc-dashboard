"""
Modelo de datos — GRC Compliance Dashboard.

Entidades principales:
- Framework: marco normativo (ISO 27001, NIST CSF, CIS).
- Control: cada control de un framework.
- Asset: activo de la organización.
- ControlAssessment: estado de implementación de un control + evidencia.
- Risk: riesgo asociado a un activo, con probabilidad e impacto.
"""

from django.conf import settings
from django.db import models


class Framework(models.Model):
    """Marco normativo de referencia (ej. ISO/IEC 27001:2022)."""

    name = models.CharField("nombre", max_length=120)
    version = models.CharField("versión", max_length=40, blank=True)
    description = models.TextField("descripción", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "marco"
        verbose_name_plural = "marcos"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "version"], name="unique_framework_version"
            )
        ]

    def __str__(self):
        return f"{self.name} {self.version}".strip()


class Control(models.Model):
    """Control individual perteneciente a un framework (ej. A.5.1)."""

    framework = models.ForeignKey(
        Framework, on_delete=models.CASCADE, related_name="controls"
    )
    code = models.CharField("código", max_length=30)
    title = models.CharField("título", max_length=255)
    domain = models.CharField("dominio", max_length=120, blank=True)
    description = models.TextField("descripción", blank=True)

    class Meta:
        verbose_name = "control"
        verbose_name_plural = "controles"
        ordering = ["framework", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["framework", "code"], name="unique_control_per_framework"
            )
        ]

    def __str__(self):
        return f"{self.code} — {self.title}"


class Asset(models.Model):
    """Activo de la organización sujeto a evaluación de seguridad."""

    class Criticality(models.TextChoices):
        LOW = "low", "Baja"
        MEDIUM = "medium", "Media"
        HIGH = "high", "Alta"
        CRITICAL = "critical", "Crítica"

    class AssetType(models.TextChoices):
        SERVER = "server", "Servidor"
        APPLICATION = "application", "Aplicación"
        DATABASE = "database", "Base de datos"
        NETWORK = "network", "Red"
        DATA = "data", "Datos / Información"
        ENDPOINT = "endpoint", "Endpoint"
        OTHER = "other", "Otro"

    name = models.CharField("nombre", max_length=150)
    asset_type = models.CharField(
        "tipo", max_length=20, choices=AssetType.choices, default=AssetType.OTHER
    )
    criticality = models.CharField(
        "criticidad",
        max_length=10,
        choices=Criticality.choices,
        default=Criticality.MEDIUM,
    )
    owner = models.CharField("responsable", max_length=120, blank=True)
    description = models.TextField("descripción", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "activo"
        verbose_name_plural = "activos"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ControlAssessment(models.Model):
    """Evaluación del estado de implementación de un control."""

    class Status(models.TextChoices):
        NOT_IMPLEMENTED = "not_implemented", "No implementado"
        PARTIAL = "partial", "Parcial"
        IMPLEMENTED = "implemented", "Implementado"
        NOT_APPLICABLE = "not_applicable", "No aplica"

    control = models.ForeignKey(
        Control, on_delete=models.CASCADE, related_name="assessments"
    )
    status = models.CharField(
        "estado",
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_IMPLEMENTED,
    )
    notes = models.TextField("notas", blank=True)
    evidence = models.FileField(
        "evidencia", upload_to="evidence/", blank=True, null=True
    )
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assessments",
    )
    assessed_at = models.DateTimeField("fecha de evaluación", auto_now=True)

    class Meta:
        verbose_name = "evaluación de control"
        verbose_name_plural = "evaluaciones de control"
        ordering = ["-assessed_at"]

    def __str__(self):
        return f"{self.control.code}: {self.get_status_display()}"


class Risk(models.Model):
    """Riesgo identificado, asociado opcionalmente a un activo."""

    class Level(models.IntegerChoices):
        VERY_LOW = 1, "Muy bajo"
        LOW = 2, "Bajo"
        MEDIUM = 3, "Medio"
        HIGH = 4, "Alto"
        VERY_HIGH = 5, "Muy alto"

    class Status(models.TextChoices):
        OPEN = "open", "Abierto"
        MITIGATING = "mitigating", "En mitigación"
        ACCEPTED = "accepted", "Aceptado"
        CLOSED = "closed", "Cerrado"

    title = models.CharField("título", max_length=200)
    description = models.TextField("descripción", blank=True)
    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="risks",
    )
    likelihood = models.IntegerField("probabilidad", choices=Level.choices)
    impact = models.IntegerField("impacto", choices=Level.choices)
    status = models.CharField(
        "estado", max_length=12, choices=Status.choices, default=Status.OPEN
    )
    treatment = models.TextField("plan de tratamiento", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "riesgo"
        verbose_name_plural = "riesgos"
        ordering = ["-created_at"]

    @property
    def risk_score(self):
        """Puntaje de riesgo = probabilidad × impacto (1–25)."""
        return self.likelihood * self.impact

    @property
    def risk_rating(self):
        """Clasificación cualitativa según el puntaje."""
        score = self.risk_score
        if score >= 15:
            return "Crítico"
        if score >= 8:
            return "Alto"
        if score >= 4:
            return "Medio"
        return "Bajo"

    def __str__(self):
        return f"{self.title} ({self.risk_rating})"

"""Configuración del admin de Django para la app compliance."""

from django.contrib import admin

from .models import Framework, Control, Asset, ControlAssessment, Risk


class ControlInline(admin.TabularInline):
    model = Control
    extra = 0
    fields = ("code", "title", "domain")


@admin.register(Framework)
class FrameworkAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "control_count", "created_at")
    search_fields = ("name", "version")
    inlines = [ControlInline]

    @admin.display(description="controles")
    def control_count(self, obj):
        return obj.controls.count()


@admin.register(Control)
class ControlAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "domain", "framework")
    list_filter = ("framework", "domain")
    search_fields = ("code", "title", "description")


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("name", "asset_type", "criticality", "owner")
    list_filter = ("asset_type", "criticality")
    search_fields = ("name", "owner")


@admin.register(ControlAssessment)
class ControlAssessmentAdmin(admin.ModelAdmin):
    list_display = ("control", "status", "assessed_by", "assessed_at")
    list_filter = ("status",)
    search_fields = ("control__code", "control__title", "notes")
    autocomplete_fields = ("control",)


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ("title", "asset", "likelihood", "impact", "risk_rating", "status")
    list_filter = ("status",)
    search_fields = ("title", "description")

    @admin.display(description="clasificación")
    def risk_rating(self, obj):
        return obj.risk_rating

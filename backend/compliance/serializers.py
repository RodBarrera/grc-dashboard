"""Serializers — convierten los modelos a JSON y validan la entrada de la API."""

from rest_framework import serializers

from .models import Framework, Control, Asset, ControlAssessment, Risk


class ControlSerializer(serializers.ModelSerializer):
    framework_name = serializers.CharField(source="framework.__str__", read_only=True)

    class Meta:
        model = Control
        fields = [
            "id",
            "framework",
            "framework_name",
            "code",
            "title",
            "domain",
            "description",
        ]


class FrameworkSerializer(serializers.ModelSerializer):
    control_count = serializers.IntegerField(source="controls.count", read_only=True)

    class Meta:
        model = Framework
        fields = ["id", "name", "version", "description", "control_count", "created_at"]


class AssetSerializer(serializers.ModelSerializer):
    asset_type_display = serializers.CharField(
        source="get_asset_type_display", read_only=True
    )
    criticality_display = serializers.CharField(
        source="get_criticality_display", read_only=True
    )

    class Meta:
        model = Asset
        fields = [
            "id",
            "name",
            "asset_type",
            "asset_type_display",
            "criticality",
            "criticality_display",
            "owner",
            "description",
            "created_at",
        ]


class ControlAssessmentSerializer(serializers.ModelSerializer):
    control_code = serializers.CharField(source="control.code", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ControlAssessment
        fields = [
            "id",
            "control",
            "control_code",
            "status",
            "status_display",
            "notes",
            "evidence",
            "assessed_by",
            "assessed_at",
        ]
        read_only_fields = ["assessed_by", "assessed_at"]


class RiskSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source="asset.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    risk_score = serializers.IntegerField(read_only=True)
    risk_rating = serializers.CharField(read_only=True)

    class Meta:
        model = Risk
        fields = [
            "id",
            "title",
            "description",
            "asset",
            "asset_name",
            "likelihood",
            "impact",
            "risk_score",
            "risk_rating",
            "status",
            "status_display",
            "treatment",
            "created_at",
        ]

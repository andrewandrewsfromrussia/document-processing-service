from rest_framework import serializers

from .models import Document


class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)


class DocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            "id",
            "original_name",
            "category",
            "detected_label",
            "status",
            "created_at",
        )


class DocumentDetailSerializer(serializers.ModelSerializer):
    file = serializers.FileField(read_only=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "original_name",
            "content_type",
            "size",
            "sha256",
            "category",
            "detected_label",
            "status",
            "error_message",
            "file",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import Document
from .serializers import (
    DocumentDetailSerializer,
    DocumentListSerializer,
    DocumentUploadSerializer,
)
from .services import detect_category, extract_text_from_upload


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Document) -> bool:
        return obj.owner_id == request.user.id


class DocumentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    filterset_fields = ("category", "status")
    ordering_fields = ("created_at", "original_name")
    ordering = ("-created_at",)

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return DocumentListSerializer
        if self.action == "retrieve":
            return DocumentDetailSerializer
        return DocumentUploadSerializer

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"file": {"type": "string", "format": "binary"}},
                "required": ["file"],
            }
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded = serializer.validated_data["file"]

        # 1) Считываем текст ДО сохранения модели (и обязательно возвращаем указатель)
        try:
            if hasattr(uploaded, "seek"):
                uploaded.seek(0)
            text = extract_text_from_upload(uploaded)
            if hasattr(uploaded, "seek"):
                uploaded.seek(0)

            category, label = detect_category(getattr(uploaded, "name", "") or "", text)

            if label == "Неизвестный документ":
                message = "Загружен неизвестный файл"
            else:
                message = f"Загружен {label.lower()}"

            doc_status = Document.Status.PROCESSED
            error_message = ""
        except Exception as e:
            # Любая ошибка парсинга -> FAILED
            category = Document.Category.OTHER
            message = "Загружен неизвестный файл"
            doc_status = Document.Status.FAILED
            error_message = str(e)

            # на всякий случай вернём указатель, чтобы файл не сохранился пустым
            if hasattr(uploaded, "seek"):
                try:
                    uploaded.seek(0)
                except Exception:
                    pass

        # 2) Сохраняем документ (файл должен быть на позиции 0)
        doc = Document.objects.create(
            owner=request.user,
            file=uploaded,
            original_name=getattr(uploaded, "name", "") or "",
            content_type=getattr(uploaded, "content_type", "") or "",
            size=getattr(uploaded, "size", 0) or 0,
            status=doc_status,
            category=category,
            detected_label=message,
            error_message=error_message,
        )

        return Response(
            {
                "id": str(doc.id),
                "message": doc.detected_label,
                "category": doc.category,
                "status": doc.status,
            },
            status=status.HTTP_201_CREATED,
        )

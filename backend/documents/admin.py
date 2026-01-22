from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "original_name",
        "category",
        "status",
        "created_at",
    )
    list_filter = ("category", "status", "created_at")
    search_fields = ("original_name", "sha256")
    readonly_fields = ("sha256", "size", "created_at", "updated_at")

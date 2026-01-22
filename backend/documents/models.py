import hashlib
import uuid

from django.conf import settings
from django.db import models


class Document(models.Model):
    class Status(models.TextChoices):
        UPLOADED = "uploaded", "Uploaded"
        PROCESSED = "processed", "Processed"
        FAILED = "failed", "Failed"

    class Category(models.TextChoices):
        RECEIPT = "receipt", "Receipt"
        CONTRACT = "contract", "Contract"
        INVOICE = "invoice", "Invoice"
        ACT = "act", "Act"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    file = models.FileField(upload_to="documents/%Y/%m/%d/")

    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255, blank=True)
    size = models.PositiveBigIntegerField(default=0)

    sha256 = models.CharField(max_length=64, blank=True)

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )
    detected_label = models.CharField(max_length=50, default="Неизвестный документ")

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADED,
    )
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _calc_sha256(self) -> str:
        h = hashlib.sha256()
        for chunk in self.file.chunks():
            h.update(chunk)
        return h.hexdigest()

    def save(self, *args, **kwargs):
        if self.file and not self.original_name:
            self.original_name = self.file.name

        if self.file:
            try:
                if not self.size:
                    self.size = self.file.size
            except Exception:
                pass

            if not self.sha256:
                try:
                    self.sha256 = self._calc_sha256()
                except Exception:
                    self.sha256 = ""

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.original_name} ({self.category})"

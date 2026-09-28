import secrets

from django.conf import settings
from django.db import models


class TokenApi(models.Model):
    """Token pembawa yang dikirim klien sendiri, terpisah dari cookie sesi."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="token_api",
    )
    key = models.CharField(max_length=64, unique=True, editable=False)
    dibuat = models.DateTimeField(auto_now_add=True)
    terakhir_dipakai = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "token API"
        verbose_name_plural = "token API"
        ordering = ["-dibuat"]

    def __str__(self):
        return f"{self.user} · {self.key[:8]}…"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(20)
        super().save(*args, **kwargs)

from django.conf import settings
from django.db import models


class Tulisan(models.Model):
    class Status(models.TextChoices):
        DRAF = "draf", "Draf"
        TERBIT = "terbit", "Terbit"

    judul = models.CharField("judul", max_length=160)
    isi = models.TextField("isi")
    penulis = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tulisan",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.DRAF,
    )
    dibuat = models.DateTimeField(auto_now_add=True)
    diubah = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-diubah"]
        permissions = [
            ("publish_tulisan", "Dapat menerbitkan tulisan"),
        ]

    def __str__(self):
        return self.judul

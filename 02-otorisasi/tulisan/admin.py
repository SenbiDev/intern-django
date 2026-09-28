from django.contrib import admin

from tulisan.models import Tulisan


@admin.register(Tulisan)
class TulisanAdmin(admin.ModelAdmin):
    list_display = ("judul", "penulis", "status", "diubah")
    list_filter = ("status",)

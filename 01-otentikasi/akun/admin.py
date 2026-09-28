from django.contrib import admin

from akun.models import TokenApi


@admin.register(TokenApi)
class TokenApiAdmin(admin.ModelAdmin):
    list_display = ("user", "key", "dibuat", "terakhir_dipakai")
    search_fields = ("user__username", "key")
    readonly_fields = ("key", "dibuat", "terakhir_dipakai")

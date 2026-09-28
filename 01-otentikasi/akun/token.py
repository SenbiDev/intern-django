from django.contrib.auth import authenticate
from django.utils import timezone

from akun.models import TokenApi


def pengguna_dari_header(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    kunci = header.removeprefix("Bearer ").strip()
    if not kunci:
        return None
    try:
        token = TokenApi.objects.select_related("user").get(key=kunci)
    except TokenApi.DoesNotExist:
        return None
    token.terakhir_dipakai = timezone.now()
    token.save(update_fields=["terakhir_dipakai"])
    return token.user


def terbitkan_token(nama, kata_sandi):
    pengguna = authenticate(username=nama, password=kata_sandi)
    if pengguna is None:
        return None
    return TokenApi.objects.create(user=pengguna)

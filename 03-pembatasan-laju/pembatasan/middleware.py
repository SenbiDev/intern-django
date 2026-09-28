from django.conf import settings
from django.http import JsonResponse
from redis.exceptions import RedisError

from pembatasan.algoritma import ALGORITMA


class BatasLajuMiddleware:
    """Berdiri di depan tampilan. Path di luar /api/ tidak dihitung."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        nama = request.GET.get("algoritma", "jendela_tetap")
        fungsi = ALGORITMA.get(nama)
        if fungsi is None:
            return JsonResponse(
                {"detail": "Algoritma tidak dikenal.", "pilihan": sorted(ALGORITMA)},
                status=400,
            )

        identitas = request.META.get("REMOTE_ADDR") or "tak-dikenal"
        aturan = settings.BATAS_LAJU
        try:
            hasil = fungsi(f"{nama}:{identitas}", aturan["batas"], aturan["periode"])
        except RedisError:
            return JsonResponse({"detail": "Redis tidak terjangkau."}, status=503)
        if hasil.diizinkan:
            respon = self.get_response(request)
        else:
            respon = JsonResponse(
                {
                    "detail": "Terlalu banyak permintaan.",
                    "algoritma": nama,
                },
                status=429,
            )
        respon["X-RateLimit-Limit"] = str(hasil.batas)
        respon["X-RateLimit-Remaining"] = str(hasil.sisa)
        respon["Retry-After"] = str(hasil.ulang_setelah)
        return respon

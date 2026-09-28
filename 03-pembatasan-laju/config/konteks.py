from django.conf import settings

from pembatasan.algoritma import redis_hidup


def lab(request):
    aturan = settings.BATAS_LAJU
    hidup = redis_hidup()
    return {
        "judul_lab": "Pembatasan laju",
        "nomor_lab": "03",
        "instrumen": [
            {"lampu": "hidup", "label": "Batas", "nilai": str(aturan["batas"])},
            {"lampu": "awas", "label": "Jendela", "nilai": f"{aturan['periode']} dtk"},
            {"lampu": "hidup" if hidup else "mati", "label": "Redis", "nilai": "hidup" if hidup else "mati"},
        ],
    }

def lab(request):
    pengguna = getattr(request, "user", None)
    masuk = bool(pengguna and pengguna.is_authenticated)
    jumlah_token = 0
    algoritma = "—"
    if masuk:
        from akun.models import TokenApi

        jumlah_token = TokenApi.objects.filter(user=pengguna).count()
        awalan = pengguna.password.split("$", 1)[0]
        algoritma = awalan or "—"
    return {
        "judul_lab": "Otentikasi",
        "nomor_lab": "01",
        "instrumen": [
            {
                "lampu": "hidup" if masuk else "mati",
                "label": "Sesi",
                "nilai": "masuk" if masuk else "tamu",
            },
            {
                "lampu": "hidup" if jumlah_token else "awas",
                "label": "Token",
                "nilai": str(jumlah_token),
            },
            {
                "lampu": "hidup" if masuk else "awas",
                "label": "Hash",
                "nilai": algoritma,
            },
        ],
    }

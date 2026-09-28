def lab(request):
    pengguna = getattr(request, "user", None)
    masuk = bool(pengguna and pengguna.is_authenticated)
    if masuk and pengguna.is_superuser:
        peran = "superuser"
        lampu = "awas"
    elif masuk:
        nama = list(pengguna.groups.values_list("name", flat=True))
        peran = ", ".join(nama) if nama else "tanpa peran"
        lampu = "hidup" if nama else "awas"
    else:
        peran = "tamu"
        lampu = "mati"
    return {
        "judul_lab": "Otorisasi",
        "nomor_lab": "02",
        "instrumen": [
            {"lampu": "hidup" if masuk else "mati", "label": "Masuk", "nilai": "ya" if masuk else "tidak"},
            {"lampu": lampu, "label": "Peran", "nilai": peran},
            {
                "lampu": "hidup" if masuk and pengguna.has_perm("tulisan.publish_tulisan") else "mati",
                "label": "Terbit",
                "nilai": "boleh" if masuk and pengguna.has_perm("tulisan.publish_tulisan") else "tidak",
            },
        ],
    }

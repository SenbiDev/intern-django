from django.contrib.auth.models import Group, Permission, User

from tulisan.models import Tulisan

AKUN_LATIHAN = {
    "pembaca": "belajar-pembaca",
    "penulis": "belajar-penulis",
    "penerbit": "belajar-penerbit",
}


def jalankan():
    grup = _grup()
    pembaca = _pengguna("pembaca", "belajar-pembaca", grup["Pembaca"])
    penulis = _pengguna("penulis", "belajar-penulis", grup["Penulis"])
    penerbit = _pengguna("penerbit", "belajar-penerbit", grup["Penerbit"])
    _pengguna(
        "admin",
        "belajar-admin",
        None,
        is_staff=True,
        is_superuser=True,
        email="admin@contoh.test",
    )
    if not Tulisan.objects.exists():
        Tulisan.objects.create(
            judul="Catatan yang sudah terbit",
            isi="Tulisan ini terlihat oleh siapa saja, termasuk tamu.",
            penulis=penulis,
            status=Tulisan.Status.TERBIT,
        )
        Tulisan.objects.create(
            judul="Draf milik penulis",
            isi="Hanya pemilik dan penerbit yang boleh melihat draf ini.",
            penulis=penulis,
            status=Tulisan.Status.DRAF,
        )
        Tulisan.objects.create(
            judul="Draf milik penerbit",
            isi="Penulis tidak boleh menyunting draf orang lain.",
            penulis=penerbit,
            status=Tulisan.Status.DRAF,
        )
    return pembaca


def pastikan_pengguna(nama):
    jalankan()
    return User.objects.get(username=nama)


def _grup():
    tulis = Permission.objects.get(codename="add_tulisan")
    ubah = Permission.objects.get(codename="change_tulisan")
    hapus = Permission.objects.get(codename="delete_tulisan")
    terbit = Permission.objects.get(codename="publish_tulisan")
    pembaca, _ = Group.objects.get_or_create(name="Pembaca")
    penulis, _ = Group.objects.get_or_create(name="Penulis")
    penerbit, _ = Group.objects.get_or_create(name="Penerbit")
    pembaca.permissions.clear()
    penulis.permissions.set([tulis, ubah])
    penerbit.permissions.set([tulis, ubah, hapus, terbit])
    return {"Pembaca": pembaca, "Penulis": penulis, "Penerbit": penerbit}


def _pengguna(nama, kata_sandi, grup, **defaults):
    pengguna, dibuat = User.objects.get_or_create(
        username=nama,
        defaults={"email": f"{nama}@contoh.test", **defaults},
    )
    if dibuat:
        pengguna.set_password(kata_sandi)
        pengguna.save()
    else:
        berubah = False
        for kunci, nilai in defaults.items():
            if getattr(pengguna, kunci) != nilai:
                setattr(pengguna, kunci, nilai)
                berubah = True
        if berubah:
            pengguna.save()
    if grup is not None:
        pengguna.groups.set([grup])
    return pengguna

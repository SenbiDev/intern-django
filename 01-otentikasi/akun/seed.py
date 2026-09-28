from django.contrib.auth.models import User


def jalankan():
    _pastikan(
        "adi",
        "belajar-adi",
        email="adi@contoh.test",
    )
    _pastikan(
        "admin",
        "belajar-admin",
        email="admin@contoh.test",
        is_staff=True,
        is_superuser=True,
    )


def _pastikan(nama, kata_sandi, **defaults):
    pengguna, dibuat = User.objects.get_or_create(username=nama, defaults=defaults)
    if dibuat:
        pengguna.set_password(kata_sandi)
        pengguna.save()
    return pengguna

"""Dua lapis otorisasi.

Izin model menjawab "apakah peran ini boleh melakukan jenis aksi ini?"
Izin objek menjawab "apakah boleh pada baris yang ini?"
Keduanya harus lolos. Superuser melewati has_perm, jadi jangan pakai
akun superuser untuk melihat perbedaan peran.
"""

from tulisan.models import Tulisan


def boleh_melihat(pengguna, tulisan):
    if tulisan.status == Tulisan.Status.TERBIT:
        return True
    if not pengguna.is_authenticated:
        return False
    if pengguna.has_perm("tulisan.publish_tulisan"):
        return True
    return tulisan.penulis_id == pengguna.id


def boleh_menyunting(pengguna, tulisan):
    if not pengguna.is_authenticated:
        return False
    if not pengguna.has_perm("tulisan.change_tulisan"):
        return False
    if pengguna.has_perm("tulisan.publish_tulisan"):
        return True
    return tulisan.penulis_id == pengguna.id


def boleh_menghapus(pengguna, tulisan):
    if not pengguna.is_authenticated:
        return False
    return pengguna.has_perm("tulisan.delete_tulisan")


def pemeriksaan(pengguna, tulisan):
    masuk = pengguna.is_authenticated
    return [
        ("Sudah masuk", masuk),
        ("Izin change_tulisan", masuk and pengguna.has_perm("tulisan.change_tulisan")),
        ("Izin publish_tulisan", masuk and pengguna.has_perm("tulisan.publish_tulisan")),
        ("Izin delete_tulisan", masuk and pengguna.has_perm("tulisan.delete_tulisan")),
        ("Pemilik objek", masuk and tulisan.penulis_id == pengguna.id),
        ("Boleh melihat", boleh_melihat(pengguna, tulisan)),
        ("Boleh menyunting", boleh_menyunting(pengguna, tulisan)),
        ("Boleh menghapus", boleh_menghapus(pengguna, tulisan)),
    ]


def terlihat_untuk(pengguna):
    terbit = Tulisan.objects.filter(status=Tulisan.Status.TERBIT)
    if not pengguna.is_authenticated:
        return terbit
    if pengguna.has_perm("tulisan.publish_tulisan"):
        return Tulisan.objects.all()
    milik = Tulisan.objects.filter(penulis=pengguna)
    return (terbit | milik).distinct()

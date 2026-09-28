"""Tiga cara menghitung permintaan, disimpan di Redis.

Waktu boleh disuntikkan supaya pengujian tidak menunggu jam dinding.
Jendela tetap memakai INCR, yang atomik di semua klien Redis.
Jendela geser memakai sorted set. Ember token memakai hash.
Dua perintah terakhir membaca lalu menulis; di produksi yang ramai
keduanya dibungkus skrip Lua supaya tidak saling menimpa.
"""

import time

from django_redis import get_redis_connection


class Hasil:
    def __init__(self, diizinkan, batas, sisa, ulang_setelah):
        self.diizinkan = diizinkan
        self.batas = batas
        self.sisa = max(0, int(sisa))
        self.ulang_setelah = max(0, int(ulang_setelah))


def _klien():
    return get_redis_connection("default")


def _teks(nilai):
    if nilai is None:
        return None
    if isinstance(nilai, bytes):
        return nilai.decode()
    return str(nilai)


def jendela_tetap(kunci, batas, periode, sekarang=None):
    sekarang = time.time() if sekarang is None else sekarang
    slot = int(sekarang) // periode
    kunci_slot = f"rl:tetap:{kunci}:{slot}"
    klien = _klien()
    jumlah = int(klien.incr(kunci_slot))
    if jumlah == 1:
        klien.expire(kunci_slot, int(periode) + 1)
    ulang = periode - (int(sekarang) % periode)
    return Hasil(jumlah <= batas, batas, batas - jumlah, ulang)


def jendela_geser(kunci, batas, periode, sekarang=None):
    sekarang = time.time() if sekarang is None else sekarang
    kunci_cache = f"rl:geser:{kunci}"
    klien = _klien()
    klien.zremrangebyscore(kunci_cache, "-inf", sekarang - periode)
    jumlah = int(klien.zcard(kunci_cache))
    if jumlah < batas:
        klien.zadd(kunci_cache, {f"{sekarang}:{time.time_ns()}": sekarang})
        klien.expire(kunci_cache, int(periode) + 1)
        return Hasil(True, batas, batas - jumlah - 1, 0)
    tertua = klien.zrange(kunci_cache, 0, 0, withscores=True)
    skor = float(tertua[0][1]) if tertua else sekarang
    ulang = max(1, int(periode - (sekarang - skor)) + 1)
    return Hasil(False, batas, 0, ulang)


def ember_token(kunci, batas, periode, sekarang=None):
    sekarang = time.time() if sekarang is None else sekarang
    laju = batas / periode
    kunci_cache = f"rl:ember:{kunci}"
    klien = _klien()
    mentah_token, mentah_terakhir = klien.hmget(kunci_cache, "token", "terakhir")
    if mentah_token is None:
        token = float(batas)
    else:
        token = min(
            float(batas),
            float(_teks(mentah_token)) + (sekarang - float(_teks(mentah_terakhir))) * laju,
        )
    if token >= 1:
        token -= 1
        diizinkan = True
        ulang = 0
    else:
        diizinkan = False
        ulang = int((1 - token) / laju) + 1
    klien.hset(kunci_cache, mapping={"token": token, "terakhir": sekarang})
    klien.expire(kunci_cache, int(periode * 2) + 1)
    return Hasil(diizinkan, batas, token, ulang)


def kosongkan():
    klien = _klien()
    kunci = list(klien.scan_iter(match="rl:*"))
    if kunci:
        klien.delete(*kunci)


def redis_hidup():
    try:
        return bool(_klien().ping())
    except Exception:
        return False


ALGORITMA = {
    "jendela_tetap": jendela_tetap,
    "jendela_geser": jendela_geser,
    "ember_token": ember_token,
}

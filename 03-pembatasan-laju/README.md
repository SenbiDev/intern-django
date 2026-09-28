# 03 — Pembatasan laju

Pembatasan laju menjaga satu klien agar tidak menghabiskan layanan. Lab ini menaruh hitungannya di **middleware**, di depan tampilan: path `/api/` dihitung, halaman percobaan tidak.

Batas latihan: **5 permintaan per 10 detik** per alamat IP. Permintaan keenam menjawab `429` dengan header `X-RateLimit-Limit`, `X-RateLimit-Remaining`, dan `Retry-After`.

Tiga algoritma ada di `pembatasan/algoritma.py` dan menulis ke Redis:

| Algoritma | Perintah Redis | Perilaku yang terlihat |
| --- | --- | --- |
| Jendela tetap | `INCR` + `EXPIRE` | Kuota habis, lalu pulih sekaligus saat slot 10 detik berganti |
| Jendela geser | sorted set `ZADD` | Cap lama jatuh satu per satu, tidak menunggu batas slot |
| Ember token | hash `HSET` | Kuota terisi kembali sedikit demi sedikit |

Redis dipakai bersama semua proses. Dua `runserver` berarti satu kuota. Rak di halaman menyala mati kalau Redis tidak terjangkau; `/api/` menjawab `503`.

## Jalankan

Redis dulu, dari folder lab ini:

```powershell
docker compose up -d
..\.venv\Scripts\python -m pip install -r requirements.txt
..\.venv\Scripts\python manage.py migrate
..\.venv\Scripts\python manage.py runserver
```

Buka <http://127.0.0.1:8000>, tekan salah satu tombol, lalu kosongkan penghitung sebelum mencoba algoritma lain. Tanpa dikosongkan, sisa kuota algoritma itu masih menempel selama jendelanya hidup.

Alamat bawaan `redis://127.0.0.1:6380/3`. Port host-nya 6380 supaya tidak menimpa Redis lain di 6379. Ganti lewat variabel lingkungan `REDIS_URL` kalau Redis Anda ada di tempat lain.

## Yang dibaca dulu

1. `pembatasan/algoritma.py`
2. `pembatasan/middleware.py`
3. `config/settings.py` — `CACHES`

## Padanan di layanan sungguhan

Gerbang, penyeimbang, atau proxy (nginx, Envoy, API gateway) yang menolak sebelum permintaan menyentuh aplikasi. Penghitungnya hampir selalu Redis, karena `INCR` atomik dan terlihat oleh setiap proses. Identitasnya alamat IP, kunci API, atau id pengguna yang sudah diautentikasi — dipilih server, bukan header yang bisa dipalsukan klien.

## Coba sendiri

1. Panggil `/api/ping/?algoritma=ember_token` dengan `curl` sebelas kali dan baca `Retry-After`.
2. Naikkan batas untuk pengguna yang sudah masuk, dan sisakan batas kecil untuk tamu.
3. Jalankan `runserver` di port 8000 dan 8001 sekaligus, habiskan kuota di salah satu, lalu panggil yang lain. Keduanya menolak.

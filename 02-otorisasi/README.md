# 02 — Otorisasi

Otentikasi sudah menjawab siapa Anda. Otorisasi menjawab **apa yang boleh Anda lakukan**.

Lab ini memisahkan dua lapisan:

- **Izin peran.** Grup Pembaca, Penulis, dan Penerbit memegang izin model Django (`add_tulisan`, `change_tulisan`, `delete_tulisan`, `publish_tulisan`).
- **Izin objek.** Penulis yang memegang `change_tulisan` tetap tidak boleh menyunting tulisan orang lain. Pemeriksaan keduanya ada di `tulisan/izin.py`, dan halaman rinci menampilkan hasilnya baris per baris.

## Jalankan

```powershell
..\.venv\Scripts\python manage.py migrate
..\.venv\Scripts\python manage.py siapkan
..\.venv\Scripts\python manage.py runserver
```

Buka <http://127.0.0.1:8000> lalu masuk lewat pilihan peran di halaman.

| Akun | Kata sandi | Peran |
| --- | --- | --- |
| `pembaca` | `belajar-pembaca` | melihat yang terbit |
| `penulis` | `belajar-penulis` | membuat dan menyunting milik sendiri |
| `penerbit` | `belajar-penerbit` | menyunting, menerbitkan, menghapus |
| `admin` | `belajar-admin` | superuser di `/admin/` |

Superuser membuat `has_perm` selalu benar. Akun itu tidak cocok untuk melihat perbedaan peran. Pintu ganti peran dikendalikan `MASUK_LATIHAN` di `config/settings.py`. Pengujian Django memaksa `DEBUG` mati, jadi pintu ini tidak menggantung pada `DEBUG`.

## Yang dibaca dulu

1. `tulisan/izin.py`
2. `tulisan/views.py` — tempat 403 dan 404 diputuskan
3. `tulisan/seed.py` — pemetaan grup ke izin

## Padanan di layanan sungguhan

Izin peran menjadi RBAC di token (scope atau claim `roles`). Izin objek menjadi pemeriksaan di layanan yang menyimpan data, karena gerbang di depan tidak tahu apakah baris nomor 14 milik peminta. Keduanya tetap dipakai bersama.

## Coba sendiri

1. Masuk sebagai penulis, buka tulisan penerbit yang sudah diterbitkan, dan baca tabel keputusan.
2. Tambah peran Korektor yang boleh menyunting tulisan siapa pun tetapi tidak boleh menerbitkan.
3. Buat izin objek untuk menghapus: penulis boleh menghapus drafnya sendiri, penerbit boleh menghapus apa pun.

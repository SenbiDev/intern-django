# 01 — Otentikasi

Otentikasi menjawab satu pertanyaan: **siapa yang meminta?** Lab ini memisahkan dua jawaban yang sering tertukar.

- **Sesi.** Setelah kata sandi cocok, server menyimpan keadaan login dan memberi browser cookie `sessionid`. Permintaan berikutnya membawa cookie itu.
- **Token.** Server memberi rahasia acak. Program lain mengirimnya sendiri di header `Authorization: Bearer …`. Tidak ada cookie.

Keduanya baru jalan setelah kata sandi lolos cek hash. Yang tersimpan di basis data adalah hash PBKDF2, bukan kata sandi.

## Jalankan

Dari folder induk repositori, lingkungan virtual cukup satu untuk semua lab.

```powershell
..\.venv\Scripts\python manage.py migrate
..\.venv\Scripts\python manage.py siapkan
..\.venv\Scripts\python manage.py runserver
```

Buka <http://127.0.0.1:8000>.

| Akun | Kata sandi | Untuk apa |
| --- | --- | --- |
| `adi` | `belajar-adi` | pengguna latihan |
| `admin` | `belajar-admin` | masuk ke `/admin/` |

Setel ulang kata sandi mencetak tautan di terminal `runserver`, ke surel `adi@contoh.test`.

## Yang dibaca dulu

1. `akun/models.py` — token pembawa.
2. `akun/token.py` — menerbitkan dan membaca header.
3. `akun/views.py` — sesi dan endpoint JSON.

## Padanan di layanan sungguhan

Halaman web tetap memakai sesi. Aplikasi seluler dan layanan lain memakai token yang masa berlakunya pendek, sering berupa JWT yang diperiksa tanda tangannya, plus token penyegar. Penyedia identitas (OIDC) menggantikan formulir login ini, tetapi hasilnya sama: sesi untuk browser, token untuk mesin.

## Coba sendiri

1. Terbitkan dua token, cabut satu, dan panggil API dengan masing-masing.
2. Tambah masa berlaku: tolak token yang `dibuat`-nya lebih tua dari satu jam.
3. Lihat di `/admin/` bahwa kolom kata sandi pengguna adalah hash, lalu bandingkan dengan rak di halaman profil.

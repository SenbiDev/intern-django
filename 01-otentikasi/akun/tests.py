from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from akun.models import TokenApi


class OtentikasiTests(TestCase):
    def setUp(self):
        self.pengguna = User.objects.create_user(
            "adi",
            email="adi@contoh.test",
            password="belajar-adi",
        )

    def test_kata_sandi_bukan_teks_polos(self):
        self.assertNotIn("belajar-adi", self.pengguna.password)
        self.assertTrue(self.pengguna.password.startswith("pbkdf2_"))

    def test_masuk_membuat_sesi(self):
        respon = self.client.post(
            "/masuk/",
            {"username": "adi", "password": "belajar-adi"},
        )
        self.assertRedirects(respon, "/profil/")
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.pengguna.pk)

    def test_kata_sandi_salah_tidak_membuat_sesi(self):
        respon = self.client.post(
            "/masuk/",
            {"username": "adi", "password": "bukan-ini"},
        )
        self.assertEqual(respon.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_token_terpisah_dari_sesi(self):
        respon = self.client.post(
            "/api/token/",
            {"username": "adi", "password": "belajar-adi"},
        )
        self.assertEqual(respon.status_code, 200)
        kunci = respon.json()["token"]
        self.assertNotIn("_auth_user_id", self.client.session)

        tolak = self.client.get("/api/profil-token/")
        self.assertEqual(tolak.status_code, 401)

        terima = self.client.get(
            "/api/profil-token/",
            HTTP_AUTHORIZATION=f"Bearer {kunci}",
        )
        self.assertEqual(terima.status_code, 200)
        self.assertEqual(terima.json()["cara"], "token")
        self.assertIsNotNone(TokenApi.objects.get(key=kunci).terakhir_dipakai)

    def test_token_yang_dicabut_ditolak(self):
        self.client.force_login(self.pengguna)
        self.client.post("/token/terbitkan/")
        token = TokenApi.objects.get(user=self.pengguna)
        self.client.post(f"/token/{token.pk}/cabut/")
        respon = self.client.get(
            "/api/profil-token/",
            HTTP_AUTHORIZATION=f"Bearer {token.key}",
        )
        self.assertEqual(respon.status_code, 401)

    def test_profil_sesi_menolak_tamu(self):
        self.assertEqual(self.client.get("/api/profil-sesi/").status_code, 401)
        self.client.force_login(self.pengguna)
        respon = self.client.get("/api/profil-sesi/")
        self.assertEqual(respon.json()["cara"], "sesi")

    def test_lupa_kata_sandi_mencetak_surel(self):
        respon = self.client.post("/kata-sandi/lupa/", {"email": "adi@contoh.test"})
        self.assertRedirects(respon, "/kata-sandi/terkirim/")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("adi", mail.outbox[0].body)

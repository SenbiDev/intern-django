from django.test import TestCase

from tulisan.models import Tulisan
from tulisan.seed import jalankan


class OtorisasiTests(TestCase):
    def setUp(self):
        jalankan()

    def _masuk(self, nama):
        respon = self.client.post("/masuk-latihan/", {"akun": nama})
        self.assertEqual(respon.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_tamu_hanya_melihat_yang_terbit(self):
        respon = self.client.get("/")
        self.assertContains(respon, "Catatan yang sudah terbit")
        self.assertNotContains(respon, "Draf milik penulis")

    def test_penulis_menyunting_miliknya(self):
        self._masuk("penulis")
        milik = Tulisan.objects.get(judul="Draf milik penulis")
        respon = self.client.post(
            f"/tulisan/{milik.pk}/sunting/",
            {"judul": "Draf milik penulis", "isi": "Isi baru."},
        )
        self.assertRedirects(respon, f"/tulisan/{milik.pk}/")
        milik.refresh_from_db()
        self.assertEqual(milik.isi, "Isi baru.")

    def test_penulis_ditolak_pada_objek_orang_lain(self):
        self._masuk("penulis")
        orang_lain = Tulisan.objects.get(judul="Catatan yang sudah terbit")
        # Terbit dan milik sendiri — buat tulisan penerbit yang terbit agar penulis bisa melihatnya.
        dari_penerbit = Tulisan.objects.get(judul="Draf milik penerbit")
        dari_penerbit.status = Tulisan.Status.TERBIT
        dari_penerbit.save()
        respon = self.client.post(
            f"/tulisan/{dari_penerbit.pk}/sunting/",
            {"judul": "Direbut", "isi": "Tidak boleh."},
        )
        self.assertEqual(respon.status_code, 403)
        dari_penerbit.refresh_from_db()
        self.assertEqual(dari_penerbit.judul, "Draf milik penerbit")
        self.assertEqual(orang_lain.judul, "Catatan yang sudah terbit")

    def test_pembaca_tidak_boleh_membuat(self):
        self._masuk("pembaca")
        respon = self.client.get("/tulis/")
        self.assertEqual(respon.status_code, 403)

    def test_penulis_tidak_boleh_menerbitkan(self):
        self._masuk("penulis")
        milik = Tulisan.objects.get(judul="Draf milik penulis")
        respon = self.client.post(f"/tulisan/{milik.pk}/terbit/")
        self.assertEqual(respon.status_code, 403)
        milik.refresh_from_db()
        self.assertEqual(milik.status, Tulisan.Status.DRAF)

    def test_penerbit_menerbitkan_dan_menyunting_milik_orang_lain(self):
        self._masuk("penerbit")
        milik = Tulisan.objects.get(judul="Draf milik penulis")
        sunting = self.client.post(
            f"/tulisan/{milik.pk}/sunting/",
            {"judul": "Disunting penerbit", "isi": milik.isi},
        )
        self.assertRedirects(sunting, f"/tulisan/{milik.pk}/")
        terbit = self.client.post(f"/tulisan/{milik.pk}/terbit/")
        self.assertRedirects(terbit, f"/tulisan/{milik.pk}/")
        milik.refresh_from_db()
        self.assertEqual(milik.status, Tulisan.Status.TERBIT)

    def test_draf_orang_lain_tidak_ketahuan(self):
        self._masuk("pembaca")
        draf = Tulisan.objects.get(judul="Draf milik penulis")
        respon = self.client.get(f"/tulisan/{draf.pk}/")
        self.assertEqual(respon.status_code, 404)

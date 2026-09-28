from unittest.mock import patch

import fakeredis
from django.test import TestCase, override_settings

from pembatasan.algoritma import ember_token, jendela_geser, jendela_tetap


class RedisCampuran(TestCase):
    def setUp(self):
        self.redis = fakeredis.FakeRedis(decode_responses=True)
        self._patch = patch("pembatasan.algoritma._klien", return_value=self.redis)
        self._patch.start()

    def tearDown(self):
        self._patch.stop()


@override_settings(BATAS_LAJU={"batas": 5, "periode": 10})
class AlgoritmaTests(RedisCampuran):
    def test_jendela_tetap_menolak_setelah_batas(self):
        hasil = [jendela_tetap("klien", 5, 10, sekarang=1_000) for _ in range(6)]
        self.assertTrue(all(item.diizinkan for item in hasil[:5]))
        self.assertFalse(hasil[5].diizinkan)
        self.assertEqual(hasil[5].sisa, 0)
        self.assertEqual(int(self.redis.get("rl:tetap:klien:100")), 6)

    def test_jendela_tetap_pulih_di_slot_berikutnya(self):
        for _ in range(5):
            jendela_tetap("klien", 5, 10, sekarang=1_000)
        self.assertFalse(jendela_tetap("klien", 5, 10, sekarang=1_009).diizinkan)
        self.assertTrue(jendela_tetap("klien", 5, 10, sekarang=1_010).diizinkan)

    def test_jendela_geser_melupakan_cap_lama(self):
        self.assertTrue(jendela_geser("klien", 2, 10, sekarang=100).diizinkan)
        self.assertTrue(jendela_geser("klien", 2, 10, sekarang=101).diizinkan)
        self.assertFalse(jendela_geser("klien", 2, 10, sekarang=102).diizinkan)
        self.assertTrue(jendela_geser("klien", 2, 10, sekarang=111).diizinkan)

    def test_ember_token_terisi_kembali(self):
        self.assertTrue(ember_token("klien", 2, 10, sekarang=0).diizinkan)
        self.assertTrue(ember_token("klien", 2, 10, sekarang=0).diizinkan)
        self.assertFalse(ember_token("klien", 2, 10, sekarang=0).diizinkan)
        pulih = ember_token("klien", 2, 10, sekarang=5)
        self.assertTrue(pulih.diizinkan)

    def test_identitas_tidak_saling_memakai_kuota(self):
        for _ in range(5):
            jendela_tetap("a", 5, 10, sekarang=100)
        self.assertFalse(jendela_tetap("a", 5, 10, sekarang=100).diizinkan)
        self.assertTrue(jendela_tetap("b", 5, 10, sekarang=100).diizinkan)


@override_settings(BATAS_LAJU={"batas": 5, "periode": 10})
class HttpTests(RedisCampuran):
    def test_halaman_tidak_dihitung(self):
        for _ in range(8):
            self.assertEqual(self.client.get("/").status_code, 200)

    def test_api_menjawab_429_beserta_header(self):
        for nomer in range(1, 6):
            respon = self.client.get("/api/ping/?algoritma=jendela_tetap")
            self.assertEqual(respon.status_code, 200, nomer)
            self.assertEqual(respon.json()["pesan"], "pong")
        ditolak = self.client.get("/api/ping/?algoritma=jendela_tetap")
        self.assertEqual(ditolak.status_code, 429)
        self.assertEqual(ditolak["X-RateLimit-Limit"], "5")
        self.assertEqual(ditolak["X-RateLimit-Remaining"], "0")
        self.assertIn("Retry-After", ditolak)

    def test_algoritma_tidak_dikenal(self):
        respon = self.client.get("/api/ping/?algoritma=ajaib")
        self.assertEqual(respon.status_code, 400)

from django.core.management.base import BaseCommand

from akun.seed import jalankan


class Command(BaseCommand):
    help = "Buat akun latihan adi dan admin jika belum ada."

    def handle(self, *args, **options):
        jalankan()
        self.stdout.write(self.style.SUCCESS("Akun latihan siap. adi / belajar-adi"))

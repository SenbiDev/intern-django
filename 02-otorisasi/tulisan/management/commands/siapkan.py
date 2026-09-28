from django.core.management.base import BaseCommand

from tulisan.seed import jalankan


class Command(BaseCommand):
    help = "Buat peran, akun latihan, dan tiga tulisan contoh."

    def handle(self, *args, **options):
        jalankan()
        self.stdout.write(self.style.SUCCESS("Peran latihan siap."))

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from tulisan.forms import TulisanForm
from tulisan.izin import (
    boleh_menghapus,
    boleh_melihat,
    boleh_menyunting,
    pemeriksaan,
    terlihat_untuk,
)
from tulisan.models import Tulisan
from tulisan.seed import AKUN_LATIHAN, pastikan_pengguna


def daftar(request):
    tulisan = terlihat_untuk(request.user)
    return render(
        request,
        "tulisan/daftar.html",
        {
            "tulisan": tulisan,
            "boleh_buat": request.user.has_perm("tulisan.add_tulisan"),
        },
    )


def rinci(request, pk):
    tulisan = get_object_or_404(Tulisan, pk=pk)
    if not boleh_melihat(request.user, tulisan):
        raise Http404("Tulisan tidak ditemukan.")
    return render(
        request,
        "tulisan/rinci.html",
        {
            "tulisan": tulisan,
            "pemeriksaan": pemeriksaan(request.user, tulisan),
            "boleh_sunting": boleh_menyunting(request.user, tulisan),
            "boleh_terbit": request.user.has_perm("tulisan.publish_tulisan"),
            "boleh_hapus": boleh_menghapus(request.user, tulisan),
        },
    )


def buat(request):
    if not request.user.is_authenticated:
        messages.error(request, "Masuk dengan akun latihan dulu.")
        return redirect("daftar")
    if not request.user.has_perm("tulisan.add_tulisan"):
        return render(
            request,
            "tulisan/tolak.html",
            {"alasan": "Peran ini tidak memegang izin add_tulisan.", "pemeriksaan": []},
            status=403,
        )
    form = TulisanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        tulisan = form.save(commit=False)
        tulisan.penulis = request.user
        tulisan.status = Tulisan.Status.DRAF
        tulisan.save()
        messages.success(request, "Draf disimpan.")
        return redirect("rinci", pk=tulisan.pk)
    return render(request, "tulisan/form.html", {"form": form, "aksi": "Tulis draf"})


@require_http_methods(["GET", "POST"])
def sunting(request, pk):
    tulisan = get_object_or_404(Tulisan, pk=pk)
    if not boleh_melihat(request.user, tulisan):
        raise Http404("Tulisan tidak ditemukan.")
    if not boleh_menyunting(request.user, tulisan):
        return render(
            request,
            "tulisan/tolak.html",
            {
                "tulisan": tulisan,
                "pemeriksaan": pemeriksaan(request.user, tulisan),
                "alasan": "Izin menyunting tidak cukup untuk objek ini.",
            },
            status=403,
        )
    form = TulisanForm(request.POST or None, instance=tulisan)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perubahan disimpan.")
        return redirect("rinci", pk=tulisan.pk)
    return render(
        request,
        "tulisan/form.html",
        {"form": form, "aksi": "Simpan perubahan", "tulisan": tulisan},
    )


@require_POST
def terbitkan(request, pk):
    tulisan = get_object_or_404(Tulisan, pk=pk)
    if not request.user.has_perm("tulisan.publish_tulisan"):
        return render(
            request,
            "tulisan/tolak.html",
            {
                "tulisan": tulisan,
                "pemeriksaan": pemeriksaan(request.user, tulisan),
                "alasan": "Peran ini tidak memegang izin publish_tulisan.",
            },
            status=403,
        )
    if tulisan.status == Tulisan.Status.TERBIT:
        tulisan.status = Tulisan.Status.DRAF
        pesan = "Tulisan dikembalikan menjadi draf."
    else:
        tulisan.status = Tulisan.Status.TERBIT
        pesan = "Tulisan diterbitkan."
    tulisan.save(update_fields=["status", "diubah"])
    messages.success(request, pesan)
    return redirect("rinci", pk=tulisan.pk)


@require_POST
def hapus(request, pk):
    tulisan = get_object_or_404(Tulisan, pk=pk)
    if not boleh_menghapus(request.user, tulisan):
        return render(
            request,
            "tulisan/tolak.html",
            {
                "tulisan": tulisan,
                "pemeriksaan": pemeriksaan(request.user, tulisan),
                "alasan": "Peran ini tidak memegang izin delete_tulisan.",
            },
            status=403,
        )
    tulisan.delete()
    messages.success(request, "Tulisan dihapus.")
    return redirect("daftar")


@require_POST
def masuk_latihan(request):
    if not getattr(settings, "MASUK_LATIHAN", False):
        raise Http404()
    nama = request.POST.get("akun", "")
    if nama not in AKUN_LATIHAN:
        messages.error(request, "Akun latihan tidak dikenal.")
        return redirect("daftar")
    pengguna = pastikan_pengguna(nama)
    login(request, pengguna, backend="django.contrib.auth.backends.ModelBackend")
    messages.success(request, f"Masuk sebagai {nama}.")
    return redirect("daftar")

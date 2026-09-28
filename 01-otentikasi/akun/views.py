import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from akun.forms import DaftarForm
from akun.models import TokenApi
from akun.token import pengguna_dari_header, terbitkan_token


def _muatan(request):
    if request.content_type == "application/json":
        try:
            data = json.loads(request.body.decode() or "{}")
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        return data
    return request.POST


def beranda(request):
    return render(request, "akun/beranda.html")


def daftar(request):
    if request.user.is_authenticated:
        return redirect("profil")
    form = DaftarForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pengguna = form.save()
        login(request, pengguna)
        messages.success(request, "Akun dibuat dan sesi dibuka.")
        return redirect("profil")
    return render(request, "akun/daftar.html", {"form": form})


@login_required
def profil(request):
    if not request.session.session_key:
        request.session.save()
    token = TokenApi.objects.filter(user=request.user)
    return render(
        request,
        "akun/profil.html",
        {
            "token_daftar": token,
            "token_terbaru": token.first(),
            "kunci_sesi": request.session.session_key,
        },
    )


@login_required
@require_POST
def terbitkan(request):
    token = TokenApi.objects.create(user=request.user)
    messages.success(request, f"Token baru terbit: {token.key}")
    return redirect("profil")


@login_required
@require_POST
def cabut(request, pk):
    token = get_object_or_404(TokenApi, pk=pk, user=request.user)
    token.delete()
    messages.success(request, "Token dicabut. Permintaan yang masih memakai token itu ditolak.")
    return redirect("profil")


@require_POST
def api_token(request):
    data = _muatan(request)
    if data is None:
        return JsonResponse({"detail": "JSON tidak valid."}, status=400)
    token = terbitkan_token(data.get("username", ""), data.get("password", ""))
    if token is None:
        return JsonResponse({"detail": "Nama atau kata sandi salah."}, status=401)
    return JsonResponse({"token": token.key, "tipe": "Bearer"})


@require_GET
def api_profil_token(request):
    pengguna = pengguna_dari_header(request)
    if pengguna is None:
        return JsonResponse({"detail": "Token tidak ada atau tidak berlaku."}, status=401)
    return JsonResponse(
        {
            "nama": pengguna.get_username(),
            "surel": pengguna.email,
            "cara": "token",
        }
    )


@require_GET
def api_profil_sesi(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Sesi belum masuk."}, status=401)
    return JsonResponse(
        {
            "nama": request.user.get_username(),
            "surel": request.user.email,
            "cara": "sesi",
        }
    )

from django.conf import settings
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from redis.exceptions import RedisError

from pembatasan.algoritma import ALGORITMA, kosongkan


def beranda(request):
    return render(
        request,
        "pembatasan/beranda.html",
        {"algoritma": ALGORITMA, "aturan": settings.BATAS_LAJU},
    )


@require_GET
def ping(request):
    return JsonResponse({"pesan": "pong", "waktu": timezone.now().isoformat()})


@require_POST
def atur_ulang(request):
    if not settings.DEBUG:
        raise Http404()
    try:
        kosongkan()
    except RedisError:
        messages.error(request, "Redis tidak terjangkau. Penghitung tidak dikosongkan.")
    return redirect("beranda")

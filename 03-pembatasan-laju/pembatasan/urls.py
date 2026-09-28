from django.urls import path

from pembatasan import views

urlpatterns = [
    path("", views.beranda, name="beranda"),
    path("atur-ulang/", views.atur_ulang, name="atur_ulang"),
    path("api/ping/", views.ping, name="ping"),
]

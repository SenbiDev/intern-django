from django.contrib.auth import views as auth_views
from django.urls import path

from tulisan import views

urlpatterns = [
    path("", views.daftar, name="daftar"),
    path("tulis/", views.buat, name="buat"),
    path("tulisan/<int:pk>/", views.rinci, name="rinci"),
    path("tulisan/<int:pk>/sunting/", views.sunting, name="sunting"),
    path("tulisan/<int:pk>/terbit/", views.terbitkan, name="terbitkan"),
    path("tulisan/<int:pk>/hapus/", views.hapus, name="hapus"),
    path("masuk-latihan/", views.masuk_latihan, name="masuk_latihan"),
    path("keluar/", auth_views.LogoutView.as_view(), name="keluar"),
]

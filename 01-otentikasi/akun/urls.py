from django.contrib.auth import views as auth_views
from django.urls import path

from akun import views

urlpatterns = [
    path("", views.beranda, name="beranda"),
    path("daftar/", views.daftar, name="daftar"),
    path(
        "masuk/",
        auth_views.LoginView.as_view(template_name="akun/masuk.html"),
        name="masuk",
    ),
    path("keluar/", auth_views.LogoutView.as_view(), name="keluar"),
    path("profil/", views.profil, name="profil"),
    path("token/terbitkan/", views.terbitkan, name="terbitkan"),
    path("token/<int:pk>/cabut/", views.cabut, name="cabut"),
    path(
        "kata-sandi/ganti/",
        auth_views.PasswordChangeView.as_view(
            template_name="akun/ganti.html",
            success_url="/profil/",
        ),
        name="ganti",
    ),
    path(
        "kata-sandi/lupa/",
        auth_views.PasswordResetView.as_view(
            template_name="akun/lupa.html",
            email_template_name="akun/surel_reset.txt",
            subject_template_name="akun/subjek_reset.txt",
            success_url="/kata-sandi/terkirim/",
        ),
        name="lupa",
    ),
    path(
        "kata-sandi/terkirim/",
        auth_views.PasswordResetDoneView.as_view(template_name="akun/terkirim.html"),
        name="terkirim",
    ),
    path(
        "kata-sandi/baru/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="akun/baru.html",
            success_url="/kata-sandi/selesai/",
        ),
        name="baru",
    ),
    path(
        "kata-sandi/selesai/",
        auth_views.PasswordResetCompleteView.as_view(template_name="akun/selesai.html"),
        name="selesai",
    ),
    path("api/token/", views.api_token, name="api_token"),
    path("api/profil-token/", views.api_profil_token, name="api_profil_token"),
    path("api/profil-sesi/", views.api_profil_sesi, name="api_profil_sesi"),
]

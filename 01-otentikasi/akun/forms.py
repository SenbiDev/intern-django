from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class DaftarForm(UserCreationForm):
    email = forms.EmailField(label="Surel")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
        labels = {"username": "Nama pengguna"}

    def save(self, commit=True):
        pengguna = super().save(commit=False)
        pengguna.email = self.cleaned_data["email"]
        if commit:
            pengguna.save()
        return pengguna

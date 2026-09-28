from django import forms

from tulisan.models import Tulisan


class TulisanForm(forms.ModelForm):
    class Meta:
        model = Tulisan
        fields = ("judul", "isi")
        labels = {"judul": "Judul", "isi": "Isi"}
        widgets = {"isi": forms.Textarea(attrs={"rows": 8})}

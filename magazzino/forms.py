from django import forms


from .models import Lotto, Pallet, Scelta, ZonaMagazzino


class LottoModelForm(forms.ModelForm):
    class Meta:
        model = Lotto
        fields = "__all__"

        widgets = {
            "codice": forms.TextInput(),
            "origine": forms.TextInput(attrs={"placeholder": "Inserisci l'origine"}),
            "pezzi": forms.NumberInput(attrs={"class": "form-control text-end"}),
            "note": forms.Textarea(
                attrs={"placeholder": "Inserisci Annotazioni", "rows": "3"}
            ),
            "created_at": forms.HiddenInput(),
            "created_by": forms.HiddenInput(),
        }
        labels = {
            "codice": "Codice",
            "origine": "Origine",
            "pezzi": "Pezzi",
            "note": "Note",
        }


class PalletModelForm(forms.ModelForm):
    fk_zona_magazzino = forms.ModelChoiceField(
        queryset=ZonaMagazzino.objects.all(),
        required=False,
        empty_label="Seleziona una zona",
        label="Zona Magazzino",
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),  # Facoltativo: Bootstrap styling
    )

    fk_scelta = forms.ModelChoiceField(
        queryset=Scelta.objects.all(),
        required=False,
        empty_label="Seleziona una scelta",
        label="Scelta",
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),  # Facoltativo: Bootstrap styling
    )

    class Meta:
        model = Pallet
        fields = "__all__"
        widgets = {
            "codice": forms.TextInput(attrs={"class": "form-control"}),
            "origine": forms.TextInput(attrs={"class": "form-control"}),
            "pezzi": forms.NumberInput(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "created_at": forms.HiddenInput(),
            "created_by": forms.HiddenInput(),
        }
        labels = {
            "codice": "Codice",
            "origine": "Origine",
            "pezzi": "Pezzi",
            "note": "Note",
            "fk_zona_magazzino": "Zona Magazzino",
            "fk_scelta": "Scelta",
        }

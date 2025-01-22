from django import forms


from .models import (
    Lotto,
    Pallet,
    Scelta,
    ZonaMagazzino,
    StockMovement,
)


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
            # "pezzi": forms.NumberInput(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "created_at": forms.HiddenInput(),
            "created_by": forms.HiddenInput(),
        }
        labels = {
            "codice": "Codice",
            "origine": "Origine",
            # "pezzi": "Pezzi",
            "note": "Note",
            "fk_zona_magazzino": "Zona Magazzino",
            "fk_scelta": "Scelta",
        }


class StockMovementModelForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "fk_lotto",
            "from_pallet",
            "to_pallet",
            "pezzi",
            "movimento",
            "fk_scelta",
            "note",
            "created_by",
        ]
        widgets = {
            "fk_lotto": forms.Select(attrs={"class": "form-control"}),
            "from_pallet": forms.Select(attrs={"class": "form-control"}),
            "to_pallet": forms.Select(attrs={"class": "form-control"}),
            "pezzi": forms.NumberInput(attrs={"class": "form-control"}),
            "movimento": forms.Select(attrs={"class": "form-control"}),
            "fk_scelta": forms.Select(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "created_by": forms.HiddenInput(),
        }
        labels = {
            "fk_lotto": "Lotto",
            "from_pallet": "Pallet di origine",
            "to_pallet": "Pallet di destinazione",
            "pezzi": "Numero di pezzi",
            "movimento": "Tipo di movimento",
            "fk_scelta": "Scelta",
            "note": "Note",
        }

    def clean(self):
        cleaned_data = super().clean()
        movimento = cleaned_data.get("movimento")
        from_pallet = cleaned_data.get("from_pallet")
        to_pallet = cleaned_data.get("to_pallet")

        # Validazione personalizzata per il tipo di movimento
        if movimento == StockMovement.OUT and not from_pallet:
            self.add_error(
                "from_pallet",
                "Per un movimento di uscita è richiesto un pallet di origine.",
            )

        if movimento == StockMovement.IN and not to_pallet:
            self.add_error(
                "to_pallet",
                "Per un movimento di ingresso è richiesto un pallet di destinazione.",
            )

        return cleaned_data

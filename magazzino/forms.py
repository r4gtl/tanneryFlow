from django import forms


from .models import (
    Lotto,
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

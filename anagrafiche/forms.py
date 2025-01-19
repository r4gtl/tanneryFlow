# from articoli.models import (Articolo, Lavorazione, ListinoCliente,
#                            ListinoTerzista, PrezzoListino)
from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from .models import (
    Cliente,
    Fornitore,
    LwgFornitore,
    DestinazioneDiversaFornitore,
    XrTransferValueLwgFornitore,
    TransferValue,
    Facility,
    FacilityContact,
)


class FormFornitore(forms.ModelForm):
    categoria = forms.ChoiceField(
        choices=Fornitore.CHOICES_CATEGORY,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = Fornitore
        # exclude=()
        fields = "__all__"
        ragionesociale = forms.CharField(max_length=100, label="Facility Name")
        indirizzo = forms.CharField()
        cap = forms.CharField()
        city = forms.CharField()
        provincia = forms.CharField()
        country = CountryField().formfield()


class FormLwgFornitore(forms.ModelForm):
    class Meta:
        model = LwgFornitore
        fields = "__all__"

        widgets = {
            "lwg_date": forms.DateInput(
                format=("%Y-%m-%d"), attrs={"class": "form-control", "type": "date"}
            ),
            "lwg_expiry": forms.DateInput(
                format=("%Y-%m-%d"), attrs={"class": "form-control", "type": "date"}
            ),
            "fk_fornitore": forms.HiddenInput(),
        }
        labels = {
            "lwg_urn": "URN",
            "lwg_score": "Punteggio",
            "lwg_range": "Fase",
            "lwg_date": "Data Certificato",
            "lwg_expiry": "Scadenza Certificato",
            "documento": "Associa Certificato",
        }


class FormXrTransferValueLwgFornitore(forms.ModelForm):
    class Meta:
        model = XrTransferValueLwgFornitore
        fields = "__all__"
        widgets = {
            "fk_lwgcertificato": forms.HiddenInput(),
            "note": forms.Textarea(
                attrs={"placeholder": "Inserisci Annotazioni", "rows": "3"}
            ),
            "created_by": forms.HiddenInput(),
        }

        labels = {
            "fk_transfervalue": "Descrizione",
            "quantity": "Quantità",
            "note": "Annotazioni",
        }


class FormTransferValue(forms.ModelForm):
    class Meta:
        model = TransferValue
        fields = "__all__"


class FormFacility(forms.ModelForm):
    class Meta:
        model = Facility
        exclude = ()
        # fields='__all__'
        nome_sito = forms.CharField(max_length=100, label="Facility Name")
        urn = forms.CharField(max_length=50, label="URN Number")
        piva = forms.CharField(max_length=11)
        indirizzo = forms.CharField(max_length=100)
        cap = forms.CharField(max_length=5)
        city = forms.CharField(max_length=100)
        provincia = forms.CharField(max_length=2)
        country = CountryField().formfield()
        phone = forms.CharField(max_length=50)
        primary_cat = forms.CharField(label="Categoria primaria")
        secondary_cat = forms.CharField(label="Categoria secondaria")
        tertiary_cat = forms.CharField(label="Categoria terziaria")
        latitude = forms.FloatField()
        longitude = forms.FloatField()
        site_area = forms.FloatField()
        facility_description = forms.Textarea()
        created_at = forms.DateTimeField()
        widgets = {
            "country": CountrySelectWidget(),
            "created_at": forms.HiddenInput(),
            "nome_sito": forms.TextInput(
                attrs={"placeholder": "Inserisci nome azienda"}
            ),
            "urn": forms.TextInput(attrs={"placeholder": "Inserisci URN"}),
            "facility_description": forms.Textarea(
                attrs={"placeholder": "Inserisci una descrizione per l'azienda"}
            ),
        }
        labels = {
            "nome_sito": "Facility Name",
            "country": "Paese",
            "primary_cat": "Categoria Primaria",
            "secondary_cat": "Categoria Secondaria",
            "tertiary_cat": "Categoria Terziaria",
            "site_area": "Superficie del Sito",
            "latitude": "Latitudine",
            "longitude": "Longitudine",
            "facility_description": "Descrizione Azienda",
        }


class FormFacilityContact(forms.ModelForm):
    class Meta:
        model = FacilityContact
        exclude = ()
        fk_facility = forms.IntegerField()
        contact_type = forms.CharField(max_length=100)
        name = forms.CharField(max_length=100)
        position = forms.CharField(max_length=100)
        email = forms.EmailField()
        widgets = {
            "fk_facility": forms.HiddenInput(),
            "name": forms.TextInput(attrs={"placeholder": "Nome e cognome"}),
            "position": forms.TextInput(attrs={"placeholder": "posizione"}),
        }


class FormCliente(forms.ModelForm):
    class Meta:
        model = Cliente
        exclude = ()
        # fields='__all__'
        ragionesociale = forms.CharField(max_length=100, label="Facility Name")
        indirizzo = forms.CharField()
        cap = forms.CharField()
        city = forms.CharField()
        provincia = forms.CharField()
        country = CountryField().formfield()

        created_by = forms.CharField()
        created_at = forms.DateTimeField()
        widgets = {
            "country": CountrySelectWidget(),
            "created_at": forms.HiddenInput(),
            "created_by": forms.HiddenInput(),
        }
        labels = {
            "ragionesociale": "Ragione Sociale",
            "country": "Paese",
            "city": "Città",
        }


class DestinazioneDiversaFornitoreModelForm(forms.ModelForm):

    class Meta:
        model = DestinazioneDiversaFornitore
        # exclude=()
        fields = "__all__"

        widgets = {
            "fk_fornitore": forms.HiddenInput(),
            "ragionesociale": forms.TextInput(),
            "indirizzo": forms.TextInput(),
            "cap": forms.TextInput(),
            "city": forms.TextInput(),
            "provincia": forms.TextInput(),
            "country": CountrySelectWidget(),
            "note": forms.Textarea(
                attrs={"placeholder": "Inserisci Annotazioni", "rows": "3"}
            ),
            "created_by": forms.HiddenInput(),
            "created_at": forms.HiddenInput(),
        }
        labels = {
            "ragionesociale": "Ragione Sociale",
            "indirizzo": "Indirizzo",
            "cap": "CAP",
            "city": "Città",
            "provincia": "Provincia",
            "country": "Paese",
            "note": "Annotazioni",
        }

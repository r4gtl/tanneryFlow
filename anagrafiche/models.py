import os
from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField  # Field from django countries app


class Cliente(models.Model):
    ragionesociale = models.CharField(max_length=50, blank=False, null=False)
    indirizzo = models.CharField(max_length=100, blank=True, null=True)
    cap = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    provincia = models.CharField(max_length=50, blank=True, null=True)
    country = CountryField(blank_label="(seleziona Paese)")
    created_by = models.ForeignKey(
        User, related_name="clienti", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ragionesociale"]

    def __str__(self):
        return self.ragionesociale

    def get_absolute_url(self):
        return reverse("anagrafiche:modifica_cliente", kwargs={"pk": self.pk})


class Fornitore(models.Model):
    #
    # Categoria
    NESSUNA = "nessuna"
    PELLI = "pelli"
    MACELLO = "macello"
    PRODOTTI_CHIMICI = "prodotti chimici"
    LAVORAZIONI_ESTERNE = "lavorazioni esterne"
    SERVIZI = "servizi"
    MANUTENZIONI = "manutenzioni"
    RIFIUTI = "rifiuti"

    CHOICES_CATEGORY = (
        (NESSUNA, "Manca categoria"),
        (PELLI, "Pelli"),
        (MACELLO, "Macello"),
        (PRODOTTI_CHIMICI, "Prodotti Chimici"),
        (LAVORAZIONI_ESTERNE, "Lavorazioni Esterne"),
        (SERVIZI, "Servizi"),
        (MANUTENZIONI, "Manutenzioni"),
        (RIFIUTI, "Rifiuti"),
    )
    ragionesociale = models.CharField(max_length=50, blank=False, null=False)
    indirizzo = models.CharField(max_length=100, blank=True, null=True)
    cap = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    provincia = models.CharField(max_length=50, blank=True, null=True)
    country = CountryField(blank_label="(seleziona Paese)")
    sito_web = models.CharField(max_length=200, blank=True, null=True)
    e_mail = models.EmailField(blank=True, null=True)
    categoria = models.CharField(
        max_length=50, choices=CHOICES_CATEGORY, default=NESSUNA
    )
    created_by = models.ForeignKey(
        User, related_name="fornitori", null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ["ragionesociale"]

    def __str__(self):
        return self.ragionesociale

    def get_absolute_url(self):
        return reverse("anagrafiche:vedi_fornitore", kwargs={"pk": self.pk})


class LwgFornitore(models.Model):
    lwg_urn = models.CharField(max_length=50)
    lwg_score = models.CharField(max_length=50, blank=True, null=True)
    lwg_range = models.CharField(max_length=100, blank=True, null=True)
    lwg_date = models.DateField(blank=True, null=True)
    lwg_expiry = models.DateField(blank=True, null=True)
    documento = models.FileField(upload_to="lwg_certificates/", null=True, blank=True)
    fk_fornitore = models.ForeignKey(Fornitore, on_delete=models.CASCADE)


class DestinazioneDiversaFornitore(models.Model):
    fk_fornitore = models.ForeignKey(
        Fornitore,
        related_name="destinazione_diversa_fornitore",
        on_delete=models.CASCADE,
    )
    ragionesociale = models.CharField(max_length=50, blank=False, null=False)
    indirizzo = models.CharField(max_length=100, blank=True, null=True)
    cap = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    provincia = models.CharField(max_length=50, blank=True, null=True)
    country = CountryField(blank_label="(seleziona Paese)")
    note = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        related_name="destinazione_diversa_fornitore",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ragionesociale"]

    def __str__(self):
        return self.ragionesociale


class TransferValue(models.Model):
    description = models.CharField(max_length=50)
    unit = models.CharField(max_length=20)

    class Meta:
        ordering = ["description"]

    def __str__(self):
        return self.description


class XrTransferValueLwgFornitore(models.Model):

    fk_lwgcertificato = models.ForeignKey(LwgFornitore, on_delete=models.CASCADE)
    fk_transfervalue = models.ForeignKey(TransferValue, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=8)
    note = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        related_name="xrtransfervaluelwgfornitore",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Facility(models.Model):
    #
    # Categorie produzione
    CAT0 = "Nessuna categoria"
    CAT1 = "A - Raw hide/skin to tanned"
    CAT2 = "B - Raw hide/skin to crust"
    CAT3 = "C - Raw hide/skin to finished leather"
    CAT4 = "D - Tanned hide/skin to finished leather"
    CAT5 = "E - Crust hide/skin to finished leather"
    CAT6 = "F - Tanned hide/skin to crust leather"
    CAT7 = "G - Raw hide/skin to pickled/pre-tanned material"

    CHOICES_PRODUCTION_CATEGORY = (
        (CAT0, "Nessuna categoria"),
        (CAT1, "A - Raw hide/skin to tanned"),
        (CAT2, "B - Raw hide/skin to crust"),
        (CAT3, "C - Raw hide/skin to finished leather"),
        (CAT4, "D - Tanned hide/skin to finished leather"),
        (CAT5, "E - Crust hide/skin to finished leather"),
        (CAT6, "F - Tanned hide/skin to crust leather"),
        (CAT7, "G - Raw hide/skin to pickled/pre-tanned material"),
    )

    nome_sito = models.CharField(max_length=100)
    logo = models.ImageField(default="avatar.png", upload_to="logo")
    urn = models.CharField(max_length=50, blank=True, null=True)
    piva = models.CharField(max_length=11, blank=True, null=True)
    indirizzo = models.CharField(max_length=100, blank=True, null=True)
    cap = models.CharField(max_length=5, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=2, blank=True, null=True)
    country = CountryField(blank_label="(seleziona Paese)")
    phone = models.CharField(max_length=50, blank=True, null=True)
    primary_cat = models.CharField(
        max_length=50, choices=CHOICES_PRODUCTION_CATEGORY, default=CAT0
    )
    secondary_cat = models.CharField(
        max_length=50, choices=CHOICES_PRODUCTION_CATEGORY, default=CAT0
    )
    tertiary_cat = models.CharField(
        max_length=50, choices=CHOICES_PRODUCTION_CATEGORY, default=CAT0
    )
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    site_area = models.FloatField(blank=True, null=True)
    facility_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_sito

    def get_absolute_url(self):
        return reverse("anagrafiche:edit_facility_details", kwargs={"pk": self.pk})


class FacilityContact(models.Model):
    #
    # Tipo Contatti
    CONT_1 = "6a - Principal Contact Name and position"
    CONT_2 = "6b - Ultimately responsible for environmental issue at this site"
    CONT_3 = (
        "6c - Responsible on a day-to-day basis for environmental issue at this site"
    )
    CONT_4 = "7 - Others"

    CHOICES_CONTACT_TYPE = (
        (CONT_1, "6a - Principal Contact Name and position"),
        (CONT_2, "6b - Ultimately responsible for environmental issue at this site"),
        (
            CONT_3,
            "6c - Responsible on a day-to-day basis for environmental issue at this site",
        ),
        (CONT_4, "7 - Others"),
    )

    fk_facility = models.ForeignKey(
        Facility, related_name="contacts", on_delete=models.CASCADE
    )
    contact_type = models.CharField(
        max_length=100, choices=CHOICES_CONTACT_TYPE, default=CONT_4
    )
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)

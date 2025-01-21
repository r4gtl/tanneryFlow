import django_filters
from django import forms

from .models import Lotto, Pallet, ZonaMagazzino, Scelta


class LottoFilter(django_filters.FilterSet):

    codice = django_filters.CharFilter(
        field_name="codice",
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"style": "width: 90%; margin-left: 5%"}),
    )
    origine = django_filters.CharFilter(
        field_name="origine",
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"style": "width: 90%; margin-left: 5%"}),
    )

    class Meta:
        model = Lotto
        fields = ["codice", "origine"]


class PalletFilter(django_filters.FilterSet):
    fk_zona_magazzino = django_filters.ModelChoiceFilter(
        queryset=ZonaMagazzino.objects.all(),
        label="Zona Magazzino",
        empty_label="Tutte le zone",  # Facoltativo, aggiunge un'opzione vuota
    )

    fk_scelta = django_filters.ModelChoiceFilter(
        queryset=Scelta.objects.all(),
        label="Scelta",
        empty_label="Tutte le scelte",  # Facoltativo, aggiunge un'opzione vuota
    )

    codice = django_filters.CharFilter(
        field_name="codice",
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"style": "width: 90%; margin-left: 5%"}),
    )
    origine = django_filters.CharFilter(
        field_name="origine",
        lookup_expr="icontains",
        widget=forms.TextInput(attrs={"style": "width: 90%; margin-left: 5%"}),
    )

    class Meta:
        model = Lotto
        fields = ["codice", "origine", "fk_scelta", "fk_zona_magazzino"]

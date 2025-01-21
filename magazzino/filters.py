import django_filters
from django import forms

from .models import (
    Lotto,
    Pallet,
    ZonaMagazzino,
    Scelta,
    StockMovement,
)


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


class StockMovementFilter(django_filters.FilterSet):
    # Filtro per la data di creazione
    created_at = django_filters.DateFromToRangeFilter(
        field_name="created_at",
        label="Intervallo di date",
        widget=django_filters.widgets.RangeWidget(
            attrs={"type": "date", "class": "form-control"}
        ),
    )

    # Filtro per il lotto
    fk_lotto = django_filters.ModelChoiceFilter(
        queryset=Lotto.objects.all(),
        label="Lotto",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    # Filtro per il pallet di origine
    from_pallet = django_filters.ModelChoiceFilter(
        queryset=Pallet.objects.all(),
        label="Dal pallet",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    # Filtro per il pallet di destinazione
    to_pallet = django_filters.ModelChoiceFilter(
        queryset=Pallet.objects.all(),
        label="Al pallet",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    # Filtro per il tipo di movimento
    movimento = django_filters.ChoiceFilter(
        choices=StockMovement.CHOICES_MOVEMENT,
        label="Tipo di movimento",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = StockMovement
        fields = ["created_at", "fk_lotto", "from_pallet", "to_pallet", "movimento"]

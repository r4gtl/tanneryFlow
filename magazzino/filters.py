import django_filters
from django import forms

from .models import Lotto


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

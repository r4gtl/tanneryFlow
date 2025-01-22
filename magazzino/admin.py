from django.contrib import admin
from .models import Scelta, ZonaMagazzino


@admin.register(Scelta)
class SceltaAdmin(admin.ModelAdmin):
    list_display = (
        "descrizione",
        "note",
        "created_at",
    )  # campi da mostrare nella lista
    search_fields = ("descrizione",)  # campi per la ricerca


@admin.register(ZonaMagazzino)
class ZonaMagazzinoAdmin(admin.ModelAdmin):
    list_display = (
        "descrizione",
        "codice",
    )  # campi da mostrare nella lista
    search_fields = ("descrizione",)  # campi per la ricerca

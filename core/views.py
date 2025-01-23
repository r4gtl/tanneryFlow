from django.shortcuts import render
from magazzino.models import Lotto, StockMovement, Pallet
from magazzino.utilities import (
    lotti_disponibili,
    get_pallets_grouped_by_scelta,
)


def home(request):
    return render(request, "core/home.html")


def dashboard(request):
    lotti_annotati = lotti_disponibili()  # Richiama la funzione
    num_lotti_disponibili = lotti_annotati.filter(net_stock__gt=0).count()
    pallets_scelta = get_pallets_grouped_by_scelta()
    context = {
        "num_lotti_disponibili": num_lotti_disponibili,
        "pallets_scelta": pallets_scelta,
    }
    return render(request, "core/dashboard.html", context)

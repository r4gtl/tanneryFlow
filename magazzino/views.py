from django.shortcuts import render
from .models import *


def home_lotti(request):
    lotti = Lotto.objects.all()
    # fornitori_filter = FornitoreFilter(request.GET, queryset=fornitori)
    # filterset_class = FornitoreFilter
    # page = request.GET.get("page", 1)
    # paginator = Paginator(
    #    fornitori_filter.qs, 50
    # )  # Utilizza fornitori_filter.qs per la paginazione

    context = {
        #'fornitori': filterset_class,
        "lotti": lotti
    }
    return render(request, "magazzino/lotti.html", context)

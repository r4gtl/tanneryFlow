from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView
from django.db.models import Sum, Subquery, OuterRef, F
from django.db.models.functions import Coalesce

from .models import *
from .forms import *
from .filters import *


# LOTTI
def home_lotti(request):
    lotti = Lotto.objects.all()
    lotti_filter = LottoFilter(request.GET, queryset=lotti)

    page = request.GET.get("page", 1)
    paginator = Paginator(
        lotti_filter.qs, 50
    )  # Utilizza lotti_filter.qs per la paginazione

    try:
        lotti_paginator = paginator.page(page)
    except PageNotAnInteger:
        lotti_paginator = paginator.page(1)
    except EmptyPage:
        lotti_paginator = paginator.page(paginator.num_pages)

    context = {
        "lotti_paginator": lotti_paginator,
        "filter": lotti_filter,
    }
    return render(request, "magazzino/home_lotti.html", context)


class LottoCreateView(LoginRequiredMixin, CreateView):
    model = Lotto
    form_class = LottoModelForm
    template_name = "magazzino/lotto.html"
    success_message = "Lotto aggiunto correttamente!"
    success_url = reverse_lazy("magazzino:home_lotti")

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)

    def get_initial(self):
        created_by = self.request.user
        print(f"User: {created_by}")
        return {
            "created_by": created_by,
        }


class LottoUpdateView(LoginRequiredMixin, UpdateView):
    model = Lotto
    form_class = LottoModelForm
    template_name = "magazzino/lotto.html"
    success_message = "Lotto modificato correttamente!"
    success_url = reverse_lazy("magazzino:home_lotti")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Aggiungi i movimenti del lotto alla context
        lotto = self.get_object()  # Ottieni l'oggetto Lotto
        movements = self.get_lotto_movements(lotto)

        context["lotto"] = lotto
        context["movements"] = movements
        return context

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)

    def get_lotto_movements(self, lotto):
        """Restituisce i movimenti 'in' del lotto raggruppati per scelta e pallet."""
        return (
            StockMovement.objects.filter(fk_lotto=lotto, movimento=StockMovement.IN)
            .values("fk_scelta__descrizione", "to_pallet__codice")
            .annotate(total_pezzi=Sum("pezzi"))
        )


def delete_lotto(request, pk):
    deleteobject = get_object_or_404(Lotto, pk=pk)
    deleteobject.delete()
    url_match = reverse_lazy("magazzino:home_lotti")
    return redirect(url_match)


# FINE LOTTI


# PALLETTS
def home_palletts(request):
    palletts = Pallet.objects.all()
    palletts_filter = PalletFilter(request.GET, queryset=palletts)

    # Sottoquery per totale in
    sub_in = (
        StockMovement.objects.filter(to_pallet=OuterRef("pk"))
        .values("to_pallet")  # Raggruppa per to_pallet
        .annotate(sum_in=Sum("pezzi"))
        .values("sum_in")
    )

    # Sottoquery per totale out
    sub_out = (
        StockMovement.objects.filter(from_pallet=OuterRef("pk"))
        .values("from_pallet")  # Raggruppa per from_pallet
        .annotate(sum_out=Sum("pezzi"))
        .values("sum_out")
    )

    # Annotiamo i pallet con total_in, total_out e net_stock
    palletts_annotated = (
        palletts_filter.qs.annotate(total_in=Coalesce(Subquery(sub_in), 0))
        .annotate(total_out=Coalesce(Subquery(sub_out), 0))
        .annotate(net_stock=F("total_in") - F("total_out"))
    )

    page = request.GET.get("page", 1)
    paginator = Paginator(palletts_annotated, 50)

    try:
        palletts_paginator = paginator.page(page)
    except PageNotAnInteger:
        palletts_paginator = paginator.page(1)
    except EmptyPage:
        palletts_paginator = paginator.page(paginator.num_pages)

    context = {
        "palletts_paginator": palletts_paginator,
        "filter": palletts_filter,
    }
    return render(request, "magazzino/home_palletts.html", context)


class PalletCreateView(LoginRequiredMixin, CreateView):
    model = Pallet
    form_class = PalletModelForm
    template_name = "magazzino/pallet.html"
    success_message = "Pallet aggiunto correttamente!"
    success_url = reverse_lazy("magazzino:home_palletts")

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)

    def get_initial(self):
        created_by = self.request.user
        return {
            "created_by": created_by,
        }

    def get_success_url(self):
        if "salva_esci" in self.request.POST:
            return reverse_lazy("magazzino:home_palletts")
        pk_pallet = self.object.pk
        print("pk_pallet: " + str(pk_pallet))
        return reverse_lazy("magazzino:modifica_pallet", kwargs={"pk": pk_pallet})


class PalletUpdateView(LoginRequiredMixin, UpdateView):
    model = Pallet
    form_class = PalletModelForm
    template_name = "magazzino/pallet.html"
    success_message = "Pallet modificato correttamente!"
    success_url = reverse_lazy("magazzino:home_palletts")

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)

    def get_success_url(self):
        if "salva_esci" in self.request.POST:
            return reverse_lazy("magazzino:home_palletts")
        pk_pallet = self.object.pk

        return reverse_lazy("magazzino:modifica_pallet", kwargs={"pk": pk_pallet})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pallet = self.object  # il pallet che stai modificando

        # Filtra i movimenti (in entrata o in uscita) che coinvolgono questo pallet
        movements = StockMovement.objects.filter(
            models.Q(from_pallet=pallet) | models.Q(to_pallet=pallet)
        ).select_related(
            "fk_lotto", "fk_scelta"
        )  # per caricare alcuni FK se servono

        context["movements"] = movements

        return context


def delete_pallet(request, pk):
    deleteobject = get_object_or_404(Pallet, pk=pk)
    deleteobject.delete()
    url_match = reverse_lazy("magazzino:home_palletts")
    return redirect(url_match)


# FINE PALLETTS


class AskMovementView(LoginRequiredMixin, TemplateView):
    template_name = "magazzino/ask_movement.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pallet_id = self.request.GET.get("pallet")
        context["pallet_id"] = pallet_id
        return context


# STOCK MOVEMENTS


def home_stock_movements(request):
    stock_movements = StockMovement.objects.all()
    stock_movements_filter = StockMovementFilter(request.GET, queryset=stock_movements)

    page = request.GET.get("page", 1)
    paginator = Paginator(
        stock_movements_filter.qs, 50
    )  # Utilizza stock_movements_filter.qs per la paginazione

    try:
        stock_movements_paginator = paginator.page(page)
    except PageNotAnInteger:
        stock_movements_paginator = paginator.page(1)
    except EmptyPage:
        stock_movements_paginator = paginator.page(paginator.num_pages)

    context = {
        "stock_movements_paginator": stock_movements_paginator,
        "filter": stock_movements_filter,
    }
    return render(request, "magazzino/home_stock_movements.html", context)


class StockMovementCreateView(LoginRequiredMixin, CreateView):
    model = StockMovement
    form_class = StockMovementModelForm
    template_name = "magazzino/stock_movement.html"
    success_message = "Movimento aggiunto correttamente!"
    # success_url = reverse_lazy("magazzino:home_stock_movements")
    # Oppure reindirizza alla pagina del pallet se preferisci

    def form_valid(self, form):
        messages.info(self.request, self.success_message)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Recupera "pallet" dalla query string
        pallet_id = self.request.GET.get("pallet")
        context["pallet_id"] = pallet_id
        return context

    def get_initial(self):
        initial = super().get_initial()

        pallet_id = self.request.GET.get("pallet")
        mtype = self.request.GET.get("mtype", "").lower()

        # Carico il pallet, se serve, per precompilare from/to
        if pallet_id:
            try:
                p = Pallet.objects.get(pk=pallet_id)
            except Pallet.DoesNotExist:
                p = None

        # Imposto i campi a seconda del tipo di movimento
        if mtype == "in":
            initial["movimento"] = "in"
            initial["to_pallet"] = p
        elif mtype == "out":
            initial["movimento"] = "out"
            initial["from_pallet"] = p
        elif mtype == "transfer":
            initial["movimento"] = "transfer"
            initial["from_pallet"] = p
        elif mtype == "sale":
            initial["movimento"] = "sale"
            initial["from_pallet"] = p
        elif mtype == "measurement":
            initial["movimento"] = "measurement"
            initial["from_pallet"] = p

        return initial

    def get_success_url(self):
        # Prova a recuperare l'ID del pallet dalla GET
        pallet_id = self.request.GET.get("pallet")
        if pallet_id:
            # Se esiste, reindirizza alla modifica del pallet
            return reverse_lazy("magazzino:modifica_pallet", kwargs={"pk": pallet_id})
        else:
            # Altrimenti usa un fallback (es. home_palletts o home_stock_movements)
            return reverse_lazy("magazzino:home_stock_movements")


class StockMovementUpdateView(LoginRequiredMixin, UpdateView):
    model = StockMovement
    form_class = StockMovementModelForm
    template_name = "magazzino/stock_movement.html"
    success_message = "Movimento modificato correttamente!"

    def get_success_url(self):
        # Recuperiamo il pallet dalla query string (se presente)
        pallet_id = self.request.GET.get("pallet")
        if pallet_id:
            # Torniamo alla view di modifica pallet con pk=pallet_id
            return reverse_lazy("magazzino:modifica_pallet", kwargs={"pk": pallet_id})
        else:
            # Se non c'è pallet, fallback su un'altra pagina
            return reverse_lazy("magazzino:home_stock_movements")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pallet_id = self.request.GET.get("pallet")
        pallet = get_object_or_404(Pallet, pk=pallet_id)
        context["pallet_id"] = pallet_id
        context["pallet"] = pallet
        return context

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)


def delete_stock_movement(request, pk):
    deleteobject = get_object_or_404(StockMovement, pk=pk)
    deleteobject.delete()
    url_match = reverse_lazy("magazzino:home_stock_movements")
    return redirect(url_match)


# FINE STOCK MOVEMENTS

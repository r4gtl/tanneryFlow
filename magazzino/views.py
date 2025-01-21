from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
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

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)


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

    page = request.GET.get("page", 1)
    paginator = Paginator(
        palletts_filter.qs, 50
    )  # Utilizza lotti_filter.qs per la paginazione

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


class PalletUpdateView(LoginRequiredMixin, UpdateView):
    model = Pallet
    form_class = PalletModelForm
    template_name = "magazzino/pallet.html"
    success_message = "Pallet modificato correttamente!"
    success_url = reverse_lazy("magazzino:home_palletts")

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)


def delete_pallet(request, pk):
    deleteobject = get_object_or_404(Pallet, pk=pk)
    deleteobject.delete()
    url_match = reverse_lazy("magazzino:home_palletts")
    return redirect(url_match)


# FINE PALLETTS

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
    success_url = reverse_lazy("magazzino:home_stock_movements")

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)

    def get_initial(self):
        created_by = self.request.user

        return {
            "created_by": created_by,
        }


class StockMovementUpdateView(LoginRequiredMixin, UpdateView):
    model = StockMovement
    form_class = StockMovementModelForm
    template_name = "magazzino/stock_movement.html"
    success_message = "Lotto modificato correttamente!"
    success_url = reverse_lazy("magazzino:home_stock_movements")

    def form_valid(self, form):
        messages.info(self.request, self.success_message)  # Compare sul success_url
        return super().form_valid(form)


def delete_stock_movement(request, pk):
    deleteobject = get_object_or_404(StockMovement, pk=pk)
    deleteobject.delete()
    url_match = reverse_lazy("magazzino:home_stock_movements")
    return redirect(url_match)


# FINE STOCK MOVEMENTS

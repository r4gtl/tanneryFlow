from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Q

import os
from datetime import date
from django.urls import reverse
from django.core.validators import MinValueValidator
from decimal import Decimal


# Create your models here.
class Scelta(models.Model):
    descrizione = models.CharField(max_length=50, blank=False, null=False)
    note = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, related_name="scelte", null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = "Scelta"  # Nome al singolare
        verbose_name_plural = "Scelte"  # Nome al plurale

    def __str__(self):
        return self.descrizione


class ZonaMagazzino(models.Model):
    descrizione = models.CharField(max_length=50, blank=False, null=False)
    codice = models.CharField(max_length=10, blank=True, null=True)
    note = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        related_name="zone_magazzino",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = "Zona Magazzino"  # Nome al singolare
        verbose_name_plural = "Zone Magazzino"  # Nome al plurale

    def __str__(self):
        return self.descrizione


class Lotto(models.Model):
    """Quando si va a creare un nuovo lotto, prevedere nella view di generare automaticamente il codice: ultimonumero+1/aa"""

    codice = models.CharField(max_length=7, null=False, blank=False)
    origine = models.CharField(max_length=50, null=True, blank=True)
    pezzi = models.PositiveIntegerField()
    note = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, related_name="lotti", null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.codice


class Pallet(models.Model):
    codice = models.CharField(max_length=10, null=False, blank=False)
    origine = models.CharField(max_length=50, null=True, blank=True)
    pezzi = models.IntegerField(null=True, blank=True)
    fk_scelta = models.ForeignKey(
        Scelta,
        related_name="palletts",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    fk_zona_magazzino = models.ForeignKey(
        ZonaMagazzino,
        related_name="palletts",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    note = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, related_name="palletts", null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.codice

    def net_stock(self):
        """Restituisce la quantità netta presente su questo pallet,
        calcolando i movimenti IN - OUT sullo stesso."""
        from .models import StockMovement  # import locale per evitare import circolari

        total_in = (
            StockMovement.objects.filter(to_pallet=self).aggregate(total=Sum("pezzi"))[
                "total"
            ]
            or 0
        )
        total_out = (
            StockMovement.objects.filter(from_pallet=self).aggregate(
                total=Sum("pezzi")
            )["total"]
            or 0
        )
        return total_in - total_out


class StockMovement(models.Model):
    # Tipo movimento
    IN = "in"
    OUT = "out"
    MEASUREMENT = "measurement"
    TRANSFER = "transfer"
    SALE = "sale"

    CHOICES_MOVEMENT = (
        (IN, "Ingresso"),
        (OUT, "Uscita"),
        (MEASUREMENT, "Misurazione"),
        (TRANSFER, "Spostamento interno"),
        (SALE, "Vendita"),
    )
    fk_lotto = models.ForeignKey(
        Lotto,
        related_name="stock_movements",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    from_pallet = models.ForeignKey(
        Pallet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements_out",
    )
    to_pallet = models.ForeignKey(
        Pallet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements_in",
    )
    pezzi = models.PositiveIntegerField()
    movimento = models.CharField(max_length=50, choices=CHOICES_MOVEMENT)
    fk_scelta = models.ForeignKey(
        Scelta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    note = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        related_name="stock_movements",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ["-created_at"]


class Misurazione(models.Model):
    fk_pallet = models.ForeignKey(
        Pallet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="measurements",
    )
    pezzi = models.PositiveIntegerField()
    mq = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.0"))],
        null=True,
        blank=True,
    )
    note = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        related_name="measurements",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ["-created_at"]

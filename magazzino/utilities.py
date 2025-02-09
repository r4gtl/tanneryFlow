from django.db.models import Sum, Case, When, F, IntegerField, Prefetch
from django.db.models.functions import Coalesce
from collections import defaultdict
from .models import Lotto, Pallet, StockMovement, Scelta


def lotti_disponibili():
    """
    Restituisce un QuerySet di tutti i lotti con:
        .total_in  = somma dei movimenti in
        .total_out = somma di TUTTI i movimenti che non sono in
        .net_stock = total_in - total_out
    E filtrati dove net_stock > 0.
    """

    lotti_annotati = (
        Lotto.objects.annotate(
            # total_in: somma di pezzi dove movimento="in"
            total_in=Coalesce(
                Sum(
                    Case(
                        When(
                            stock_movements__movimento="in",
                            then=F("stock_movements__pezzi"),
                        ),
                        default=0,
                        output_field=IntegerField(),
                    )
                ),
                0,
            ),
            # total_out: somma di pezzi dove movimento != "in"
            total_out=Coalesce(
                Sum(
                    Case(
                        When(
                            stock_movements__movimento="in",
                            # Se è "in", allora non li contiamo qui (quindi 0)
                            then=0,
                        ),
                        # Tutti gli altri casi (out, transfer, sale, measurement, ecc.)
                        # li consideriamo "uscite"
                        default=F("stock_movements__pezzi"),
                        output_field=IntegerField(),
                    )
                ),
                0,
            ),
        )
        # Aggiungiamo net_stock come differenza
        .annotate(net_stock=F("total_in") - F("total_out"))
        # Filtriamo i soli lotti con net_stock > 0
        .filter(net_stock__gt=0)
    )

    return lotti_annotati


def get_pallets_with_total_in_and_out_old():
    """
    Eseguiamo la prima query per ottenere i totali in entrata e in uscita per ciascun pallet.
    """
    return Pallet.objects.annotate(
        total_in=Sum(
            "movements_in__pezzi",
            filter=StockMovement.objects.filter(
                to_pallet=F("pk"), movimento=StockMovement.IN
            ),
            default=0,
        ),
        total_out=Sum(
            "movements_out__pezzi",
            filter=StockMovement.objects.filter(
                from_pallet=F("pk"), movimento=StockMovement.OUT
            ),
            default=0,
        ),
    ).values(
        "id", "fk_scelta", "fk_scelta__descrizione", "total_in", "total_out"
    )  # Otteniamo solo i campi necessari


def get_pallets_grouped_by_scelta_old():
    """
    Restituisce i pallet raggruppati per fk_scelta e la somma della rimanenza netta.
    """
    # Prima query: otteniamo i totali in entrata e in uscita per ogni pallet
    pallets_with_stock = get_pallets_with_total_in_and_out()

    # Elaborazione dei dati in Python per calcolare la somma netta per ciascun pallet
    grouped_data = defaultdict(int)

    for pallet in pallets_with_stock:
        net_stock = pallet["total_in"] - pallet["total_out"]
        # Sommiamo la rimanenza netta per ogni fk_scelta
        grouped_data[pallet["fk_scelta"]] += net_stock

    # Otteniamo la descrizione della Scelta per ogni fk_scelta
    scelte = {scelta.id: scelta.descrizione for scelta in Scelta.objects.all()}

    # Convertiamo i dati raggruppati in una lista di dizionari
    result = [
        {
            "fk_scelta": fk_scelta,
            "descrizione": scelte.get(fk_scelta, "Descrizione non trovata"),
            "total_net_stock": total_net_stock,
        }
        for fk_scelta, total_net_stock in grouped_data.items()
    ]

    return result


def get_pallets_with_total_in_and_out():
    """
    Restituisce i pallet con i totali in entrata e in uscita.
    """
    pallets = Pallet.objects.all()
    result = []

    # Calcoliamo manualmente il totale in entrata e in uscita per ciascun pallet
    for pallet in pallets:
        total_in = (
            StockMovement.objects.filter(
                to_pallet=pallet, movimento=StockMovement.IN
            ).aggregate(Sum("pezzi"))["pezzi__sum"]
            or 0
        )
        total_out = (
            StockMovement.objects.filter(
                from_pallet=pallet, movimento=StockMovement.OUT
            ).aggregate(Sum("pezzi"))["pezzi__sum"]
            or 0
        )
        result.append(
            {
                "pallet": pallet,
                "total_in": total_in,
                "total_out": total_out,
            }
        )

    return result


def get_pallets_grouped_by_scelta():
    """
    Restituisce i pallet raggruppati per fk_scelta e la somma della rimanenza netta.
    """
    # Prima query: otteniamo i totali in entrata e in uscita per ogni pallet
    pallets_with_stock = get_pallets_with_total_in_and_out()

    # Raggruppiamo per fk_scelta
    grouped_data = defaultdict(int)

    for pallet_data in pallets_with_stock:
        # Verifica se fk_scelta è None
        if pallet_data["pallet"].fk_scelta is not None:
            net_stock = pallet_data["total_in"] - pallet_data["total_out"]
            grouped_data[
                pallet_data["pallet"].fk_scelta.id
            ] += net_stock  # Raggruppiamo usando l'ID della Scelta
        else:
            # Se fk_scelta è None, possiamo decidere cosa fare (es. ignorare o fare altro)
            print(f"Pallet {pallet_data['pallet'].codice} senza fk_scelta")

    # Otteniamo la descrizione della Scelta per ogni fk_scelta
    scelte = {scelta.id: scelta.descrizione for scelta in Scelta.objects.all()}

    # Convertiamo i dati raggruppati in una lista di dizionari
    result = [
        {
            "fk_scelta": fk_scelta,
            "descrizione": scelte.get(
                fk_scelta, "Descrizione non trovata"
            ),  # Otteniamo la descrizione
            "total_net_stock": total_net_stock,
        }
        for fk_scelta, total_net_stock in grouped_data.items()
    ]

    return result

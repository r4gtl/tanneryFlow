from django.urls import path
from .views import *


app_name = "magazzino"


urlpatterns = [
    # Lotto
    path("lotti/", home_lotti, name="home_lotti"),
    path("aggiungi_lotto/", LottoCreateView.as_view(), name="aggiungi_lotto"),
    path("modifica_lotto/<int:pk>/", LottoUpdateView.as_view(), name="modifica_lotto"),
    path("delete_lotto/<int:pk>/", delete_lotto, name="delete_lotto"),
    # Pallet
    path("palletts/", home_palletts, name="home_palletts"),
    path("aggiungi_pallet/", PalletCreateView.as_view(), name="aggiungi_pallet"),
    path(
        "modifica_pallet/<int:pk>/", PalletUpdateView.as_view(), name="modifica_pallet"
    ),
    path("delete_pallet/<int:pk>/", delete_pallet, name="delete_pallet"),
]

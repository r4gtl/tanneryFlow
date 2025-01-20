from django.urls import path
from .views import *


app_name = "magazzino"


urlpatterns = [
    # Facility
    path(
        "lotti/",
        home_lotti,
        name="home_lotti",
    ),
]

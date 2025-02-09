"""
WSGI config for tanneryFlow project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""
'''
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanneryFlow.settings')

application = get_wsgi_application()
'''

import os

import environ
from django.core.wsgi import get_wsgi_application

# Inizializza environ per gestire le variabili d'ambiente
env = environ.Env()
environ.Env.read_env()  # Legge il file .env


#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tannerySuite.settings')
# Imposta il modulo delle impostazioni in base alla variabile d'ambiente
django_env = env('DJANGO_ENV', default='development')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"tanneryFlow.settings.{django_env}")

application = get_wsgi_application()
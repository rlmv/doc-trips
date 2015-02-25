"""
WSGI config for doc_fyt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "doc.settings")

import sys
from django.conf import settings
BASE_DIR = settings.BASE_DIR
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

application = get_wsgi_application()
application = DjangoWhiteNoise(application)


from splinter.browser import Browser
from django.test import Client, TestCase
from django.test.utils import setup_test_environment, teardown_test_environment
from django.db import connection
import django

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','doc-trips.settings')

import sys
from django.conf import settings
BASE_DIR = settings.BASE_DIR
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

def before_all(context):

    django.setup()

def before_scenario(context, scenario):

    # We must set up and tear down the entire database between
    # scenarios. We can't just use db transactions, as Django's
    # TestClient does, if we're doing full-stack tests with Mechanize,
    # because Django closes the db connection after finishing the HTTP
    # response.

    setup_test_environment()
    context.old_db_config = connection.creation.create_test_db()

    context.browser = Browser('django')
    context.client = Client()
    context.test = TestCase()

def after_scenario(context, scenario):
    # Tear down the scenario test environment.

    connection.creation.destroy_test_db(context.old_db_config)
    teardown_test_environment()

    context.browser.quit()
    context.browser = None
    context.client = None



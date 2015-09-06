# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def init_settings(apps, schema_editor):

    Settings = apps.get_model('incoming', 'Settings')
    TripsYear = apps.get_model('db', 'TripsYear')
    Settings.objects.create(
        trips_year=TripsYear.objects.get(year=2015),
        trips_cost=235,
        doc_membership_cost=50,
        contact_url="http://outdoors.dartmouth.edu/firstyear/contact.html"
    )


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0013_auto_20150906_1106'),
    ]

    operations = [
        migrations.RunPython(init_settings)
    ]

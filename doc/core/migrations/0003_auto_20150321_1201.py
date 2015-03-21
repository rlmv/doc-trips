# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def init_settings(apps, schema_editor):

    Settings = apps.get_model('core', 'Settings')
    Settings.objects.create(
        trips_cost=220, doc_membership_cost=50, 
        contact_url='http://outdoors.dartmouth.edu/firstyear/contact.html'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150321_1201'),
    ]

    operations = [
        migrations.RunPython(init_settings)
    ]

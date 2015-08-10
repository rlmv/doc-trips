# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def init_raidinfo(apps, schema_editor):
    RaidInfo = apps.get_model('raids', 'RaidInfo')
    TripsYear = apps.get_model('db', 'TripsYear')
    RaidInfo.objects.get_or_create(trips_year=TripsYear.objects.get(is_current=True))
  

class Migration(migrations.Migration):

    dependencies = [
        ('raids', '0005_auto_20150810_1151')
    ]

    operations = [
        migrations.RunPython(init_raidinfo)
    ]

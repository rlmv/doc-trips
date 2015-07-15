# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from doc.utils.lat_lng import parse_lat_lng

def parse_lat_lng_from_Stop_address(apps, schema_editor):

    Stop = apps.get_model('transport', 'Stop')

    for stop in Stop.objects.all():
        coords = parse_lat_lng(stop.address)
        if coords:
            stop.lat_lng = coords
            print('found %s' % coords)
            stop.save()

class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0028_stop_lat_lng'),
    ]

    operations = [
        migrations.RunPython(parse_lat_lng_from_Stop_address)
    ]

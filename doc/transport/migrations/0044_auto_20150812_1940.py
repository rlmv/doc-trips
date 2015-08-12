# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def migrate_one_way_cost(apps, schema_editor):

    Stop = apps.get_model('transport', 'Stop')

    for stop in Stop.objects.all():

        split = stop.name.split('(one way: FROM HANOVER)')
        if len(split) == 2:
            target = split[0].strip()
            print(target)
            target = Stop.objects.get(name=target)
            target.cost_one_way = stop.cost_round_trip
            target.save()

        split = stop.name.split('(one way: TO HANOVER)')
        if len(split) == 2:
            target = split[0].strip()
            print(target)
            target = Stop.objects.get(name=target)
            target.cost_one_way = stop.cost_round_trip
            target.save()


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0043_auto_20150812_1905'),
    ]

    operations = [
        migrations.RunPython(migrate_one_way_cost)
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def one_way_bus_stops(apps, schema_editor):
    """ 
    Use bus_stop_to_hanover and bus_stop_from_hanover instead
    of one-way bus stops.
    """
    Registration = apps.get_model('incoming', 'Registration')
    Stop = apps.get_model('transport', 'Stop')

    for reg in Registration.objects.all():
        stop = reg.bus_stop_round_trip

        if not stop:
            continue

        split = stop.name.split('(one way: FROM HANOVER)')
        if len(split) == 2:
            target = split[0].strip()
            print("%s -- %s" % (reg.name, target))
            reg.bus_stop_from_hanover = Stop.objects.get(name=target)
            reg.bus_stop_round_trip = None

        split = stop.name.split('(one way: TO HANOVER)')
        if len(split) == 2:
            target = split[0].strip()
            print("%s -- %s" % (reg.name, target))
            reg.bus_stop_to_hanover = Stop.objects.get(name=target)
            reg.bus_stop_round_trip = None
        reg.save()


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0008_auto_20150814_1654'),
    ]

    operations = [
        migrations.RunPython(one_way_bus_stops)
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def one_way_bus_stops(apps, schema_editor):

    IncomingStudent = apps.get_model('incoming', 'IncomingStudent')
    Stop = apps.get_model('transport', 'Stop')

    for inc in IncomingStudent.objects.all():
        stop = inc.bus_assignment

        if not stop:
            continue

        split = stop.name.split('(one way: FROM HANOVER)')
        if len(split) == 2:
            target = split[0].strip()
            print(target)
            inc.bus_assignment_from_hanover = Stop.objects.get(name=target)

        split = stop.name.split('(one way: TO HANOVER)')
        if len(split) == 2:
            target = split[0].strip()
            print(target)
            inc.bus_assignment_to_hanover = Stop.objects.get(name=target)
        inc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0002_auto_20150812_1738'),
    ]

    operations = [
        migrations.RunPython(one_way_bus_stops)
    ]

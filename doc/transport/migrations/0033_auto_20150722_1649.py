# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion

def non_null_distance(apps, schema_editor):
    Stop = apps.get_model('transport', 'Stop')
    for stop in Stop.objects.filter(distance=None):
        stop.distance = 0
        stop.save()

class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('transport', '0032_auto_20150715_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='StopOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('distance', models.PositiveSmallIntegerField(blank=True)),
                ('bus', models.ForeignKey(to='transport.ScheduledTransport')),
                ('stop', models.ForeignKey(to='transport.Stop')),
                ('trips_year', models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(non_null_distance),
        migrations.AlterField(
            model_name='stop',
            name='distance',
            field=models.IntegerField(help_text='this rough distance from Hanover is used for bus routing'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('transport', '0020_auto_20150324_1326'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledTransport',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('date', models.DateField()),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='transport.Route')),
                ('trips_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='scheduledtransportation',
            name='route',
        ),
        migrations.RemoveField(
            model_name='scheduledtransportation',
            name='trips_year',
        ),
        migrations.DeleteModel(
            name='ScheduledTransportation',
        ),
    ]

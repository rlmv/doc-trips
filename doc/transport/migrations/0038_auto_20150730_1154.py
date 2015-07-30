# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('trips', '0032_auto_20150728_1315'),
        ('transport', '0037_auto_20150729_2246'),
    ]

    operations = [
        migrations.CreateModel(
            name='StopOrder',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('order', models.PositiveSmallIntegerField(blank=True)),
                ('stop_type', models.CharField(choices=[('PICKUP', 'PICKUP'), ('DROPOFF', 'DROPOFF')], max_length=10)),
                ('bus', models.ForeignKey(to='transport.ScheduledTransport')),
                ('trip', models.ForeignKey(to='trips.Trip')),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False, on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='stoporder',
            unique_together=set([('trips_year', 'bus', 'trip')]),
        ),
    ]

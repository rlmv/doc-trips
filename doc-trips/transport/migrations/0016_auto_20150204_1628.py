# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0015_auto_20150129_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='route',
            name='vehicle',
            field=models.ForeignKey(to='transport.Vehicle', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='scheduledtransportation',
            name='route',
            field=models.ForeignKey(to='transport.Route', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='scheduledtransportation',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='stop',
            name='route',
            field=models.ForeignKey(null=True, blank=True, to='transport.Route', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='stop',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0003_croo_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='croo',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='crooapplication',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='crooapplicationanswer',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='crooapplicationgrade',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='crooapplicationquestion',
            name='trips_year',
            field=models.ForeignKey(editable=False, to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]

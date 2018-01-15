# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('trips', '0011_auto_20151015_1230'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='')),
                ('template', models.ForeignKey(to='trips.TripTemplate', on_delete=models.CASCADE)),
                ('trips_year', models.ForeignKey(editable=False, to='core.TripsYear', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

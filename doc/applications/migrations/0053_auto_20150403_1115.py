# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        ('applications', '0052_auto_20150320_1146'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortalContent',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('day0_description', models.TextField(blank=True, verbose_name='day 0 description')),
                ('day1_description', models.TextField(blank=True)),
                ('day5_description', models.TextField(blank=True)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='portalcontent',
            unique_together=set([('trips_year',)]),
        ),
    ]

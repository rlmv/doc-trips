# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0017_auto_20150310_1431'),
        ('croos', '0010_auto_20150310_1152'),
        ('applications', '0051_auto_20150319_2311'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='croosupplement',
            name='assigned_croo',
        ),
        migrations.RemoveField(
            model_name='croosupplement',
            name='kitchen_lead',
        ),
        migrations.RemoveField(
            model_name='croosupplement',
            name='kitchen_lead_qualified',
        ),
        migrations.RemoveField(
            model_name='croosupplement',
            name='potential_croos',
        ),
        migrations.RemoveField(
            model_name='croosupplement',
            name='safety_lead',
        ),
        migrations.RemoveField(
            model_name='croosupplement',
            name='safety_lead_qualified',
        ),
        migrations.RemoveField(
            model_name='leadersupplement',
            name='assigned_trip',
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='assigned_croo',
            field=models.ForeignKey(to='croos.Croo', null=True, blank=True, related_name='croolings', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='assigned_trip',
            field=models.ForeignKey(to='trips.ScheduledTrip', null=True, blank=True, related_name='leaders', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
    ]

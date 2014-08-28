# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0006_auto_20140725_1847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderapplication',
            name='assigned_trip',
            field=models.ForeignKey(related_name='leaders', to='trip.ScheduledTrip', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='available_sections',
            field=models.ManyToManyField(related_name='+', to='trip.Section', blank=True),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='preferred_sections',
            field=models.ManyToManyField(related_name='+', to='trip.Section', blank=True),
        ),
        migrations.AlterField(
            model_name='leadergrade',
            name='leader_application',
            field=models.ForeignKey(related_name='grades', to='leader.LeaderApplication'),
        ),
    ]

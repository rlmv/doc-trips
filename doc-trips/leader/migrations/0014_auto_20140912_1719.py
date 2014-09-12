# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0013_auto_20140912_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderapplication',
            name='applied_to_trips',
            field=models.BooleanField(verbose_name='Have you applied to lead a Trip before?', default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='is_in_hanover_this_fall',
            field=models.BooleanField(verbose_name='Are you planning to be in Hanover this fall?', default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='personal_activities',
            field=models.TextField(verbose_name='Please list your primary activities and involvements at Dartmouth and beyond', default='', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='personal_communities',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='tell_us_about_yourself',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='went_on_trip',
            field=models.BooleanField(verbose_name='Did you go on a First Year Trip?', default=False),
            preserve_default=True,
        ),
    ]

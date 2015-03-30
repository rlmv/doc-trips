# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0013_auto_20150320_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='anything_else',
            field=models.TextField(verbose_name="Is there any other information you'd like to provide (anything helps!) that would assist us in assigning you to a trip?", blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='boating_experience',
            field=models.TextField(verbose_name='Please describe your canoe or kayak trip experience. Have you paddled on flat water? Have you paddled on flat water? When did you do these trips and how long were they?', blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='bus_stop',
            field=models.ForeignKey(verbose_name='Where would you like to be bussed from/to?', null=True, on_delete=django.db.models.deletion.PROTECT, blank=True, to='transport.Stop'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='fishing_experience',
            field=models.TextField(verbose_name='Please describe your fishing experience.', blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='has_boating_experience',
            field=models.CharField(max_length=2, default='NO', choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Have you ever been on an overnight or extended canoe or kayak trip?'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='horseback_riding_experience',
            field=models.TextField(verbose_name='Please describe your riding experience and ability level. What riding styles are you familiar with? How recently have you ridden horses on a regular basis? NOTE: Prior exposure and some experience is preferred for this trip.', blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='mountain_biking_experience',
            field=models.TextField(verbose_name='Please describe your biking experience and ability level. Have you done any biking off of paved trails? How comfortable are you riding on dirt and rocks?', blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='other_boating_experience',
            field=models.TextField(verbose_name='Please describe any other paddling experience you have had. Be specific regarding location, type of water, and distance covered.', blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='swimming_ability',
            field=models.CharField(max_length=20, choices=[('NON_SWIMMER', 'Non-Swimmer'), ('BEGINNER', 'Beginner'), ('COMPETENT', 'Competent'), ('EXPERT', 'Expert')], verbose_name='Please rate yourself as a swimmer'),
        ),
    ]

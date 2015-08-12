# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0042_auto_20150812_1125'),
        ('incoming', '0001_squashed_0049_auto_20150806_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomingstudent',
            name='bus_assignment_from_hanover',
            field=models.ForeignKey(blank=True, related_name='riders_from_hanover', to='transport.Stop', null=True, on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='bus_assignment_to_hanover',
            field=models.ForeignKey(blank=True, related_name='riders_to_hanover', to='transport.Stop', null=True, on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='bus_assignment',
            field=models.ForeignKey(blank=True, related_name='riders_round_trip', to='transport.Stop', null=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='registration',
            name='allergy_reaction',
            field=models.TextField(verbose_name='If you have a food allergy, please describe what happens when you come into contact with the allergen (e.g. I get hives, I go into anaphylactic shock).', blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='epipen',
            field=models.CharField(verbose_name='Do you carry an EpiPen? If yes, please bring it with you on Trips.', max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='sailing_experience',
            field=models.TextField(verbose_name='Please describe your sailing experience.', blank=True),
        ),
    ]

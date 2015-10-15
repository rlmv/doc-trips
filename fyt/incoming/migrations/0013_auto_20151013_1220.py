# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0012_auto_20151013_1057'),
    ]

    operations = [
        migrations.RemoveField(model_name='registration', name='epipen'),
        migrations.AlterField(
            model_name='registration',
            name='food_allergies',
            field=models.TextField(verbose_name="Please list any food allergies you have (e.g. peanuts, shellfish). Describe what happens when you come into contact with this allergen (e.g. 'I get hives', 'I go into anaphylactic shock').", blank=True, help_text='Leave blank if not applicable'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='medical_conditions',
            field=models.TextField(verbose_name='Do you have any other medical conditions, past injuries, disabilities or other allergies that we should be aware of? Please describe any injury, condition, disability, or illness which we should take into consideration in assigning you to a trip', blank=True, help_text='Leave blank if not applicable'),
        ),
    ]

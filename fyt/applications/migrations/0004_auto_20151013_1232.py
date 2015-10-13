# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0003_auto_20150910_1512'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='generalapplication',
            name='allergen_information',
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='epipen',
            field=models.NullBooleanField(verbose_name='Do you carry an EpiPen? If yes, please bring it with you on Trips.', choices=[(True, 'Yes'), (False, 'No')], default=None),
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='food_allergies',
            field=models.TextField(verbose_name="Please list any food allergies you have (e.g. peanuts, shellfish). Describe what happens when you come into contact with this allergen (e.g. 'I get hives', 'I go into anaphylactic shock').", blank=True, help_text='Leave blank if not applicable'),
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='medical_conditions',
            field=models.TextField(verbose_name='Do you have any other medical conditions, past injuries, disabilities or other allergies that we should be aware of? Please describe any injury, condition, disability, or illness which we should take into consideration in assigning you to a trip', blank=True, help_text='Leave blank if not applicable'),
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='needs',
            field=models.TextField(verbose_name='While many students manage their own health needs, we would prefer that you let us know of any other needs or conditions so we can ensure your safety and comfort during the trip (e.g. Diabetes, recent surgery, migraines).', blank=True, help_text='Leave blank if not applicable'),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='dietary_restrictions',
            field=models.TextField(verbose_name='Do you have any other dietary restrictions we should be aware of (vegetarian, gluten-free, etc.)? We can accommodate ANY and ALL dietary needs as long as we know in advance.', blank=True, help_text='Leave blank if not applicable'),
        ),
    ]

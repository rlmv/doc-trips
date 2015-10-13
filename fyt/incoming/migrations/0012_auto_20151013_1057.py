# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0011_auto_20150918_1932'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registration',
            name='allergen_information',
        ),
        migrations.RemoveField(
            model_name='registration',
            name='allergies',
        ),
        migrations.RemoveField(
            model_name='registration',
            name='allergy_reaction',
        ),
        migrations.RemoveField(
            model_name='registration',
            name='allergy_severity',
        ),
        migrations.AddField(
            model_name='registration',
            name='food_allergies',
            field=models.TextField(verbose_name="Please list any food allergies you have (e.g. peanuts, shellfish). Describe what happens when you come into contact with this allergen (e.g. 'I get hives, I go into anaphylactic shock).", blank=True, help_text='Leave blank if not applicable'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='dietary_restrictions',
            field=models.TextField(verbose_name='Do you have any other dietary restrictions we should be aware of (vegetarian, gluten-free, etc.)? We can accommodate ANY and ALL dietary needs as long as we know in advance.', blank=True, help_text='Leave blank if not applicable'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='medical_conditions',
            field=models.TextField(verbose_name='Do you have any other medical conditions, past injuries, disabilities or allergies that we should be aware of? Please describe any injury, condition, disability, or illness which we should take into consideration in assigning you to a trip', blank=True, help_text='Leave blank if not applicable'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='needs',
            field=models.TextField(verbose_name='While many students manage their own health needs, we would prefer that you let us know of any other needs or conditions so we can ensure your safety and comfort during the trip (e.g. Diabetes, recent surgery, migraines).', blank=True, help_text='Leave blank if not applicable'),
        ),
    ]

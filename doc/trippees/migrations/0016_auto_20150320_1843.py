# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trippees', '0015_auto_20150320_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='allergen_information',
            field=models.TextField(blank=True, verbose_name='What happens if you come into contact with this allergen (e.g. I get hives, I go into anaphylactic shock)?'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='allergies',
            field=models.TextField(blank=True, verbose_name='Please describe any allergies you have (e.g. bee stings, specific medications, foods, etc.) which might require special medical attention.'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='dietary_restrictions',
            field=models.TextField(blank=True, verbose_name='Do you have any dietary restrictions we should be aware of (vegetarian, gluten-free, etc.)? We can accommodate ANY and ALL dietary needs as long as we know in advance. Leave blank if not applicable'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='medical_conditions',
            field=models.TextField(blank=True, verbose_name='Do you have any medical conditions, past injuries, disabilities or allergies that we should be aware of? Please describe any injury, condition, disability, or illness which we should take into consideration in assigning you to a trip'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='needs',
            field=models.TextField(blank=True, verbose_name='While many students manage their own health needs, we would prefer that you let us know of any other needs or conditions so we can ensure your safety and comfort during the trip.'),
        ),
    ]

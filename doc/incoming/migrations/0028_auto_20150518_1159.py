# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0027_auto_20150518_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='allergy_reaction',
            field=models.TextField(default='', verbose_name='If you have a food allergy, please describe what happens when you come into contact with the allergen (e.g. I get hives, I go into anaphylactic shock).', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='allergy_severity',
            field=models.PositiveIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name='If you have a food allergy, please rate the severity of the allergy on a scale from 1 to 5 (1 = itchy skin, puffy eyes and 5 = anaphylaxis).', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='needs',
            field=models.TextField(verbose_name='While many students manage their own health needs, we would prefer that you let us know of any other needs or conditions so we can ensure your safety and comfort during the trip (e.g. Diabetes, recent surgery, migraines).', blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0062_auto_20150512_2055'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadersupplement',
            name='community_building',
            field=models.DateField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leadersupplement',
            name='first_aid',
            field=models.DateField(verbose_name='First Aid/CPR', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leadersupplement',
            name='risk_management',
            field=models.DateField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leadersupplement',
            name='wilderness_skills',
            field=models.DateField(blank=True, null=True),
            preserve_default=True,
        ),
    ]

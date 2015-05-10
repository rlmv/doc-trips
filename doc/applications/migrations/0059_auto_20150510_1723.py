# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0058_auto_20150420_0208'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leadersupplement',
            name='community_building',
        ),
        migrations.RemoveField(
            model_name='leadersupplement',
            name='first_aid',
        ),
        migrations.RemoveField(
            model_name='leadersupplement',
            name='risk_management',
        ),
        migrations.RemoveField(
            model_name='leadersupplement',
            name='wilderness_skills',
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='community_building',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='croo_training',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='first_aid',
            field=models.CharField(max_length=10, default='', choices=[(None, None)], blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='first_aid_other',
            field=models.CharField(max_length=100, default='', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='risk_management',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='wilderness_skills',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0026_auto_20150330_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='epipen',
            field=models.CharField(verbose_name='Do you carry an EpiPen? If yes, please bring it with you on Trips.', choices=[('YES', 'yes'), ('NO', 'no')], blank=True, max_length=3, default='NO'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='registration',
            name='is_international',
            field=models.CharField(verbose_name='Are you an International who plans on attending the International Student Orientation?', blank=True, max_length=3, choices=[('YES', 'yes'), ('NO', 'no')]),
        ),
        migrations.AlterField(
            model_name='registration',
            name='is_native',
            field=models.CharField(verbose_name='Are you a Native American Student who plans on attending the Native American student orientation?', blank=True, max_length=3, choices=[('YES', 'yes'), ('NO', 'no')]),
        ),
    ]

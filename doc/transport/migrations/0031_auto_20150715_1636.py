# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import doc.utils.lat_lng


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0030_auto_20150715_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stop',
            name='lat_lng',
            field=models.CharField(validators=[doc.utils.lat_lng.validate_lat_lng], verbose_name='coordinates', max_length=255, default='', blank=True, help_text='Latitude & longitude coordinates, eg. 43.7030,-72.2895'),
        ),
    ]

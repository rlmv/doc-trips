# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0007_auto_20151015_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campsite',
            name='bugout',
            field=models.TextField(help_text='directions for quick help', blank=True),
        ),
        migrations.AlterField(
            model_name='campsite',
            name='secret',
            field=models.TextField(help_text='door codes and other secret info', blank=True),
        ),
    ]

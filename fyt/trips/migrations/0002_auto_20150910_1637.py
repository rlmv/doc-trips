# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campsite',
            name='bugout',
            field=models.TextField(help_text='directions for quick help'),
        ),
        migrations.AlterField(
            model_name='campsite',
            name='secret',
            field=models.TextField(help_text='door codes and other secret information'),
        ),
    ]

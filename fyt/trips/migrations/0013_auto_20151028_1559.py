# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0012_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='template',
            field=models.ForeignKey(related_name='documents', to='trips.TripTemplate'),
        ),
    ]

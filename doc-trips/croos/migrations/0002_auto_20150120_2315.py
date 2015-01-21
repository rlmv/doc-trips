# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crooapplication',
            name='answers',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, null=True, to='croos.CrooApplicationAnswer'),
        ),
    ]

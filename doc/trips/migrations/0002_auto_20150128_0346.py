# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='triptemplate',
            old_name='trip_type',
            new_name='triptype',
        ),
        migrations.AlterField(
            model_name='section',
            name='name',
            field=models.CharField(help_text='A, B, C, etc.', max_length=1, verbose_name='Section'),
        ),
    ]

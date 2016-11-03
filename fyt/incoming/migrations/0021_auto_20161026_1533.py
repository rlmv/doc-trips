# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0020_auto_20161025_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptypechoice',
            name='preference',
            field=models.CharField(choices=[('FIRST CHOICE', 'first choice'), ('PREFER', 'prefer'), ('AVAILABLE', 'available'), ('NOT AVAILABLE', 'not available')], max_length=20),
        ),
    ]

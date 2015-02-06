# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import croos.models


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0005_auto_20150205_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crooapplicationgrade',
            name='grade',
            field=models.IntegerField(validators=[croos.models.validate_grade]),
        ),
    ]

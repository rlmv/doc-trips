# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0017_auto_20150310_1431'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='triptemplate',
            options={'ordering': ['name']},
        ),
    ]

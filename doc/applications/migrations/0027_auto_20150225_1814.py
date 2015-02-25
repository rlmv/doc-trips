# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0026_auto_20150222_2208'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='generalapplication',
            options={'ordering': ('applicant',)},
        ),
    ]

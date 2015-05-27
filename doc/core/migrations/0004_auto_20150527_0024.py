# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150321_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='contact_url',
            field=models.URLField(help_text='url of trips directorate contact info'),
        ),
    ]

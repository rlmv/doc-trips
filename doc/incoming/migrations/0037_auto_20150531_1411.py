# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import doc.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0036_auto_20150527_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='netid',
            field=doc.users.models.NetIdField(max_length=20),
        ),
    ]

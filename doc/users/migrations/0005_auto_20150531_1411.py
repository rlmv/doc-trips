# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import doc.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20150420_1014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dartmouthuser',
            name='netid',
            field=doc.users.models.NetIdField(max_length=20, unique=True),
        ),
    ]

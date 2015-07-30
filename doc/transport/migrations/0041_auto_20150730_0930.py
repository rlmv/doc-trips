# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0040_remove_stoporder_stop'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stoporder',
            options={'ordering': ['order']},
        ),
        migrations.RenameField(
            model_name='stoporder',
            old_name='distance',
            new_name='order',
        ),
    ]

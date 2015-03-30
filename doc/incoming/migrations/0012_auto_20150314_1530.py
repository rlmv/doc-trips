# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0011_auto_20150314_1320'),
    ]

    operations = [
        migrations.RenameField(
            model_name='incomingstudent',
            old_name='dartmouth_email',
            new_name='blitz',
        ),
    ]

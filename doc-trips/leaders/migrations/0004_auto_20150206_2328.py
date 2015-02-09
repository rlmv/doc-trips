# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leaders', '0003_auto_20150204_1628'),
    ]

    operations = [
        migrations.RenameField('LeaderApplication', 'user', 'applicant')
    ]

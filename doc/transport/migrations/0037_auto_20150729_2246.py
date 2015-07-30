# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0032_auto_20150728_1315'),
        ('transport', '0036_auto_20150727_1826'),
    ]

    operations = [
        migrations.DeleteModel('StopOrder')
    ]

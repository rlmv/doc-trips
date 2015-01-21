# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0005_auto_20150121_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crooapplicationanswer',
            name='application',
            field=models.ForeignKey(to='croos.CrooApplication', editable=False, related_name='answers'),
        ),
    ]

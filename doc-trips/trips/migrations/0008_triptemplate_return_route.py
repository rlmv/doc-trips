# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0015_auto_20150129_2039'),
        ('trips', '0007_auto_20150129_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='triptemplate',
            name='return_route',
            field=models.ForeignKey(related_name='returning_trips', default=1, to='transport.Route'),
            preserve_default=False,
        ),
    ]

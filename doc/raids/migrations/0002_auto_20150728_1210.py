# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raids', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='raid',
            field=models.ForeignKey(editable=False, to='raids.Raid', default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='raid',
            name='plan',
            field=models.TextField(blank=True),
        ),
    ]

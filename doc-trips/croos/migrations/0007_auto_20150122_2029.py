# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0006_auto_20150121_1924'),
    ]

    operations = [
        migrations.RenameField(
            model_name='crooapplicationgrade',
            old_name='croo_application',
            new_name='application',
        ),
        migrations.AddField(
            model_name='crooapplicationgrade',
            name='comments',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='crooapplicationgrade',
            name='grade',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]

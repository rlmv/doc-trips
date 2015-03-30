# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0006_auto_20150311_1336'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trippee',
            name='user',
        ),
        migrations.AlterField(
            model_name='trippee',
            name='info',
            field=models.OneToOneField(editable=False, related_name='trippee', to='incoming.TrippeeInfo'),
        ),
        migrations.AlterField(
            model_name='trippee',
            name='registration',
            field=models.OneToOneField(editable=False, related_name='trippee', null=True, to='incoming.TrippeeRegistration'),
        ),
    ]

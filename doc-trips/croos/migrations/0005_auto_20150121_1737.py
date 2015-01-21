# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0004_auto_20150120_2322'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crooapplication',
            name='answers',
        ),
        migrations.AddField(
            model_name='crooapplicationanswer',
            name='application',
            field=models.ForeignKey(related_name='answers', to='croos.CrooApplication', default=1),
            preserve_default=False,
        ),
    ]

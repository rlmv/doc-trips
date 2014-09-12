# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0010_auto_20140911_0002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderapplication',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='leadergrade',
            name='grader',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]

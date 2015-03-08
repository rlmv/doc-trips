# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0038_auto_20150306_1833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crooapplicationgrade',
            name='grader',
            field=models.ForeignKey(editable=False, related_name='crooapplicationgrade', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='leaderapplicationgrade',
            name='grader',
            field=models.ForeignKey(editable=False, related_name='leaderapplicationgrade', to=settings.AUTH_USER_MODEL),
        ),
    ]

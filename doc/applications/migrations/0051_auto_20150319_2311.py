# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0050_auto_20150317_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalapplication',
            name='applicant',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, related_name='applications'),
        ),
    ]

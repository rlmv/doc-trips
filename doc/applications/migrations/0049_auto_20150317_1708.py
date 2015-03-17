# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('applications', '0048_skippedcroograde_skippedleadergrade'),
    ]

    operations = [
        migrations.AddField(
            model_name='skippedcroograde',
            name='grader',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='skippedleadergrade',
            name='grader',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL, editable=False),
            preserve_default=False,
        ),
    ]

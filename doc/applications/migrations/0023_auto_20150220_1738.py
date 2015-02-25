# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import doc.applications.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0022_croograde_leadergrade'),
    ]

    operations = [
        migrations.AddField(
            model_name='croograde',
            name='application',
            field=models.ForeignKey(to='applications.CrooSupplement', related_name='grades', editable=False, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leadergrade',
            name='application',
            field=models.ForeignKey(to='applications.LeaderSupplement', related_name='grades', editable=False, default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='croograde',
            name='comment',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='croograde',
            name='grade',
            field=models.PositiveSmallIntegerField(validators=[doc.applications.models.validate_grade]),
        ),
        migrations.AlterField(
            model_name='croograde',
            name='grader',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False),
        ),
        migrations.AlterField(
            model_name='leadergrade',
            name='comment',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='leadergrade',
            name='grade',
            field=models.PositiveSmallIntegerField(validators=[doc.applications.models.validate_grade]),
        ),
        migrations.AlterField(
            model_name='leadergrade',
            name='grader',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False),
        ),
    ]

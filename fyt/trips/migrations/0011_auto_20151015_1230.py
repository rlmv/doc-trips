# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0010_auto_20151015_1216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='triptemplate',
            name='non_swimmers_allowed',
        ),
        migrations.AlterField(
            model_name='triptemplate',
            name='swimtest_required',
            field=models.BooleanField(help_text="if selected, available trippees will be at least 'BEGINNER' swimmers", default=False),
        ),
    ]

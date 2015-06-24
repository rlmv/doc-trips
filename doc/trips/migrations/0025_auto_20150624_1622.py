# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0024_auto_20150505_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptemplate',
            name='non_swimmers_allowed',
            field=models.BooleanField(help_text="otherwise, trippees on the assignment page will be those who are at least 'BEGINNER' swimmers", verbose_name='non-swimmers allowed', default=True),
        ),
    ]

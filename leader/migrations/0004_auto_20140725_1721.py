# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import leader.models


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0003_auto_20140724_0425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leadergrade',
            name='grade',
            field=models.DecimalField(decimal_places=1, max_digits=3, validators=[leader.models.validate_grade]),
        ),
    ]

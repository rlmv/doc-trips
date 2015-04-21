# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import doc.trips.models


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0020_auto_20150420_1010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triptemplate',
            name='name',
            field=models.PositiveSmallIntegerField(db_index=True, validators=[doc.trips.models.validate_triptemplate_name]),
        ),
    ]

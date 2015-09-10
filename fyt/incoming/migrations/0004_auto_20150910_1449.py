# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fyt.incoming.models


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0003_auto_20150909_2313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='waiver',
            field=models.CharField(validators=[fyt.incoming.models.validate_waiver], max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='I certify that I have read this assumption of risk and the accompanying registration materials. I approve participation for the student indicated above and this serves as my digital signature of this release, waiver and acknowledgement.'),
        ),
    ]

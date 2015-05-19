# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0030_auto_20150518_1251'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registration',
            name='cell_phone',
        ),
        migrations.RemoveField(
            model_name='registration',
            name='home_phone',
        ),
        migrations.AddField(
            model_name='registration',
            name='phone',
            field=models.CharField(default=1, blank=True, verbose_name='phone number', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='registration',
            name='waiver',
            field=models.CharField(choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='I certify that I have read this assumption of risk and the accompanying registration materials. I approve participation for the student indicated above and this serves as my digital signature of this release, waiver and acknowledgement.', max_length=3),
        ),
    ]

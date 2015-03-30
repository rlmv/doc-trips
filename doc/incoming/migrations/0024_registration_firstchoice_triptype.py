# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0017_auto_20150310_1431'),
        ('incoming', '0023_auto_20150325_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='firstchoice_triptype',
            field=models.ForeignKey(related_name='firstchoice_triptype', blank=True, null=True, to='trips.Section'),
            preserve_default=True,
        ),
    ]

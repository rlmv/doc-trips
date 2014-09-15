# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0016_auto_20140912_2033'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leaderapplication',
            name='offcampus_address',
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='gender',
            field=models.CharField(max_length=25),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='hinman_box',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='spring_leader_training_ok',
            field=models.BooleanField(verbose_name='I can attend Leader Training during the spring term.', default=False),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='summer_leader_training_ok',
            field=models.BooleanField(verbose_name='I can attend Leader Training during the summer term.', default=False),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0011_auto_20140912_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderapplication',
            name='answer_confidentiality',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='answer_from',
            field=models.CharField(verbose_name='Where are you from?', max_length=255, default='hi'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='answer_goodstanding',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='answer_study',
            field=models.CharField(verbose_name='What do you like to study?', max_length=255, default='hi'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='offcampus_address',
            field=models.CharField(blank=True, verbose_name='Where can we reach you this summer?', max_length=255),
        ),
    ]

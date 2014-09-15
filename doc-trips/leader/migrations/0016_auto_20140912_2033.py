# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0015_auto_20140912_2016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaderapplication',
            name='spring_leader_training_ok',
            field=models.BooleanField(default=False, verbose_name='Yes, I can attend Leader Training during the spring term.'),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='summer_leader_training_ok',
            field=models.BooleanField(default=False, verbose_name='Yes, I can attend Leader Training during the summer term.'),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='trip_preference_comments',
            field=models.TextField(verbose_name='Looking at the Trips descriptions, please feel free to use this space to address any concerns or explain your availability. This will only be used to help us in Trip assignments, it will not be considered when your application is being read.', blank=True),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='what_to_change_about_trips',
            field=models.TextField(verbose_name='If you have led a DOC Trip before, what would you change about the program (big or small)? If you have not led a DOC Trip before, what would you change about the program (big or small) OR what would you change about your introduction to Dartmouth?', blank=True),
        ),
    ]

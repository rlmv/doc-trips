# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0032_auto_20150303_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crooapplicationgrade',
            name='grade',
            field=models.PositiveSmallIntegerField(verbose_name='score', choices=[(1, "1 -- Bad application -- I really don't want this person to be a volunteer and I have serious concerns"), (2, '2 -- Poor application -- I have some concerns about this person being a Trips volunteer'), (3, '3 -- Fine application -- This person might work well as a volunteer but I have some questions'), (4, "4 -- Good application -- I would consider this person to be a volunteer but I wouldn't be heartbroken if they were not selected"), (5, '5 -- Great application -- I think this person would be a fantastic volunteer'), (6, '6 -- Incredible application -- I think this person should be one of the first to be selected to be a volunteer. I would be very frustrated/angry if this person is not selected')]),
        ),
        migrations.AlterField(
            model_name='leaderapplicationgrade',
            name='grade',
            field=models.PositiveSmallIntegerField(verbose_name='score', choices=[(1, "1 -- Bad application -- I really don't want this person to be a volunteer and I have serious concerns"), (2, '2 -- Poor application -- I have some concerns about this person being a Trips volunteer'), (3, '3 -- Fine application -- This person might work well as a volunteer but I have some questions'), (4, "4 -- Good application -- I would consider this person to be a volunteer but I wouldn't be heartbroken if they were not selected"), (5, '5 -- Great application -- I think this person would be a fantastic volunteer'), (6, '6 -- Incredible application -- I think this person should be one of the first to be selected to be a volunteer. I would be very frustrated/angry if this person is not selected')]),
        ),
    ]

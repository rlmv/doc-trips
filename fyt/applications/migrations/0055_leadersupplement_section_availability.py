# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-21 22:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0054_auto_20170221_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadersupplement',
            name='section_availability',
            field=models.TextField(blank=True, verbose_name='Students that plan to attend pre-orientation programs or are transfer/exchange students will be placed on particular sections, as indicated above. If you would like to lead a trip on a section with these students, please indicate your preference here.'),
        ),
    ]

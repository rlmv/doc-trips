# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0009_auto_20151230_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalapplication',
            name='leadership_style',
            field=models.TextField(verbose_name='Describe your leadership style and your role in a group. Please go to <a href="https://sites.google.com/a/stgregoryschool.org/mr-roberts/home/theoretical-and-applied-leadership/leadership-squares">this website</a> and use the four descriptions (Puzzle Master, Director, Coach, or Diplomat) as a framework for your answer. Please order the four leadership styles in order of how much you identify with each one of them, and use them as a launching pad to discuss your strengths and weaknesses. This is not supposed to box you in to a specific category, but rather it serves to provide you with a structure to discuss your strengths and weaknesses and group-work styles so that we can effectively pair you with a co-leader or fellow croolings who complements you. Each leadership style is equally valuable, and we will use answers to this question to balance our teams as a whole.', default=''),
            preserve_default=False,
        ),
    ]

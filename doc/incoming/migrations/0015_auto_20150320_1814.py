# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0014_auto_20150320_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='final_request',
            field=models.TextField(verbose_name='We know this form is really long, so thanks for sticking with us! The following question has nothing to do with your trip assignment. To whatever extent you feel comfortable, please share one thing you are excited and/or nervous for about coming to Dartmouth (big or small). There is no right or wrong answers &mdash; anything goes! All responses will remain anonymous.'),
        ),
    ]

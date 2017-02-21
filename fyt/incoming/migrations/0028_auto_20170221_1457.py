# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-21 19:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0027_auto_20170220_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrationsectionchoice',
            name='preference',
            field=models.CharField(choices=[('PREFER', 'prefer'), ('AVAILABLE', 'available'), ('NOT AVAILABLE', 'not available')], default='NOT AVAILABLE', max_length=20),
        ),
        migrations.AlterField(
            model_name='registrationtriptypechoice',
            name='preference',
            field=models.CharField(choices=[('FIRST CHOICE', 'first choice'), ('PREFER', 'prefer'), ('AVAILABLE', 'available'), ('NOT AVAILABLE', 'not available')], default='NOT AVAILABLE', max_length=20),
        ),
    ]
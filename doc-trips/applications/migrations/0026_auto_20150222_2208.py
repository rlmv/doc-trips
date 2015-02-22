# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0025_auto_20150221_0018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalapplication',
            name='medical_certifications',
            field=models.TextField(verbose_name='Current trainings in First Aid and CPR are required for all DOC trip leaders and croo members. Please list any relevant medical certifications you hold (e.g. First Aid, CPR, Wilderness First Aid, Wilderness First Responder, Emergency Medical Technician, Wilderness Emergency Medical Technician, Outdoor Emergency Care). Also list the program that sponsored the certification, and the dates they expire. If you do not currently have such a certification (or if your certification will expire before Trips ends), we will be in touch about how you can get trained through Trips-sponsored First Aid & CPR courses in the spring and summer.', blank=True, help_text="eg. 'First Aid - American Red Cross, expires October 2013.'"),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0002_auto_20150216_1723'),
    ]

    operations = [
        migrations.RenameField(
            model_name='leadersupplement',
            old_name='experience',
            new_name='relevant_experience',
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='medical_certifications',
            field=models.TextField(verbose_name="Current trainings in First Aid and CPR are required for all DOC trip leaders and croo members. Please list any relevant medical certifications you currently hold, the program that sponsored the certification and the dates they expire — for example, 'First Aid - American Red Cross, expires October 2013.' If you do not currently have such a certification (or if your certification will expire before Trips ends), we will be in touch about how you can get trained before trips begin. DOC Trips will offer several First Aid & CPR courses in the spring and summer.)", help_text='First Aid, CPR, Wilderness First Aid, Wilderness First Responder, Emergency Medical Technician (EMT), Wilderness Emergency Medical Technician (W-EMT), Outdoor Emergency Care (OEC)', blank=True),
        ),
    ]

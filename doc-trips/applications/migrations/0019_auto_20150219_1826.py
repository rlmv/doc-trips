# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0018_auto_20150219_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalapplication',
            name='medical_certifications',
            field=models.TextField(blank=True, verbose_name='Current trainings in First Aid and CPR are required for all DOC trip leaders and croo members. Please list any relevant medical certifications you hold, eg. First Aid, CPR, Wilderness First Aid, Wilderness First Responder, Emergency Medical Technician (EMT), Wilderness Emergency Medical Technician (W-EMT), Outdoor Emergency Care (OEC); the program that sponsored the certification, and the dates they expire. If you do not currently have such a certification (or if your certification will expire before Trips ends), we will be in touch about how you can get trained before trips begin. DOC Trips will offer several First Aid & CPR courses in the spring and summer.)', help_text="eg. 'First Aid - American Red Cross, expires October 2013.'"),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='role_preference',
            field=models.CharField(verbose_name="While Trips Directorate will ultimately decide where we think you will be most successful in the program, we would like to know your preferences. If you are submitting a Trip Leader application AND a Croo application, please indicate which position you prefer. If you are only applying to one position, please choose 'N/A'", max_length=20, default='N/A', choices=[('PREFER_LEADER', 'Prefer Trip Leader'), ('PREFER_CROO', 'Prefer Croo'), ('N/A', 'N/A')]),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='trippee_confidentiality',
            field=models.BooleanField(verbose_name="If selected to be a Trips Leader or a Croo member, I understand that I will be given access to Trippees' confidential medical information for safety purposes. I pledge to maintain the confidentiality of this information, except as is required by medical or legal concerns", default=False),
        ),
    ]

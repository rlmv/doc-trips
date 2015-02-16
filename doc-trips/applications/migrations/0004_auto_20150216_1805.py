# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0003_auto_20150216_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='croosupplement',
            name='application',
            field=models.OneToOneField(related_name='croo_supplement', to='applications.GeneralApplication'),
        ),
        migrations.AlterField(
            model_name='croosupplement',
            name='document',
            field=models.FileField(blank=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='medical_certifications',
            field=models.TextField(help_text="eg. 'First Aid - American Red Cross, expires October 2013.'", verbose_name='Current trainings in First Aid and CPR are required for all DOC trip leaders and croo members. Please list any relevant medical certifications (eg. First Aid, CPR, Wilderness First Aid, Wilderness First Responder, Emergency Medical Technician (EMT), Wilderness Emergency Medical Technician (W-EMT), Outdoor Emergency Care (OEC)) you currently hold, the program that sponsored the certification and the dates they expire. If you do not currently have such a certification (or if your certification will expire before Trips ends), we will be in touch about how you can get trained before trips begin. DOC Trips will offer several First Aid & CPR courses in the spring and summer.)', blank=True),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='peer_training',
            field=models.TextField(verbose_name='List and briefly describe any peer training program (DPP, IGD, DBI, MAV, EDPA, SAPA, DAPA, UGA, etc.) that you have lead or participated in.', blank=True),
        ),
        migrations.AlterField(
            model_name='leadersupplement',
            name='application',
            field=models.OneToOneField(related_name='leader_supplement', to='applications.GeneralApplication'),
        ),
        migrations.AlterField(
            model_name='leadersupplement',
            name='supplement',
            field=models.FileField(verbose_name='Leader supplement', blank=True, upload_to=''),
        ),
    ]

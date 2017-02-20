# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-20 19:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0037_auto_20170220_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalapplication',
            name='medical_certifications',
            field=models.TextField(blank=True, help_text="eg. 'First Aid - American Red Cross, expires October 2013.'", verbose_name='Please list any relevant medical certifications you hold (e.g. First Aid, CPR, Wilderness First Aid, Wilderness First Responder, Emergency Medical Technician, Wilderness Emergency Medical Technician, Outdoor Emergency Care). Also list the program that sponsored the certification, and the dates they expire.'),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='medical_experience',
            field=models.TextField(blank=True, verbose_name='Briefly describe your experience using your medical certifications. How frequently do you use your certifications and in what circumstances?'),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='peer_training',
            field=models.TextField(blank=True, verbose_name='List and briefly describe any peer training program (e.g. DPP, IGD, DBI, MAV, EDPA, SAPA, DAPA, UGA, etc.) that you have lead or participated in.'),
        ),
    ]

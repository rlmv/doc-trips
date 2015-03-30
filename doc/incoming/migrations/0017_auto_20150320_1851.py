# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0016_auto_20150320_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='camping_experience',
            field=models.CharField(max_length=3, verbose_name='Have you ever spent a night camping in the outdoors?', choices=[('YES', 'yes'), ('NO', 'no')]),
        ),
        migrations.AlterField(
            model_name='registration',
            name='doc_membership',
            field=models.CharField(max_length=3, verbose_name='Would you like to purchase a DOC membership?', choices=[('YES', 'yes'), ('NO', 'no')]),
        ),
        migrations.AlterField(
            model_name='registration',
            name='final_request',
            field=models.TextField(verbose_name='We know this form is really long, so thanks for sticking with us! The following question has nothing to do with your trip assignment. To whatever extent you feel comfortable, please share one thing you are excited and/or nervous for about coming to Dartmouth (big or small). There is no right or wrong answers &mdash; anything goes! All responses will remain anonymous.', blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='financial_assistance',
            field=models.CharField(max_length=3, verbose_name="Are you requesting financial assistance from DOC Trips? If 'yes' we will contact you in July with more information about your financial assistance.", choices=[('YES', 'yes'), ('NO', 'no')]),
        ),
        migrations.AlterField(
            model_name='registration',
            name='green_fund_donation',
            field=models.PositiveSmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='has_boating_experience',
            field=models.CharField(max_length=3, verbose_name='Have you ever been on an overnight or extended canoe or kayak trip?', blank=True, choices=[('YES', 'yes'), ('NO', 'no')]),
        ),
        migrations.AlterField(
            model_name='registration',
            name='hiking_experience',
            field=models.CharField(max_length=3, verbose_name='Have you ever hiked or climbed with a pack of at least 20-30 pounds (10-15 kilograms)?', choices=[('YES', 'yes'), ('NO', 'no')]),
        ),
        migrations.AlterField(
            model_name='registration',
            name='waiver',
            field=models.CharField(max_length=3, verbose_name='I certify that I have read this assumption of risk and the accompanying registration materials. I approve participation for the student indicated above and this serves as my digital signature of this release, waiver & acknowledgement.', choices=[('YES', 'yes'), ('NO', 'no')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0007_auto_20150217_0426'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationinformation',
            name='croo_application_introduction',
            field=models.TextField(blank=True, default='', help_text='This will be displayed at the top of Croo Application tab'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applicationinformation',
            name='leader_application_introduction',
            field=models.TextField(blank=True, default='', help_text='This will be displayed at the top of the Leader Application tab'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='applicationinformation',
            name='croo_supplement_questions',
            field=models.FileField(verbose_name='Croo Application questions', help_text='.docx file', upload_to=''),
        ),
        migrations.AlterField(
            model_name='applicationinformation',
            name='leader_supplement_questions',
            field=models.FileField(verbose_name='Leader Application questions', help_text='.docx file', upload_to=''),
        ),
        migrations.AlterField(
            model_name='croosupplement',
            name='document',
            field=models.FileField(blank=True, verbose_name='Croo Application Answers', upload_to=''),
        ),
        migrations.AlterField(
            model_name='croosupplement',
            name='kitchen_lead_willing',
            field=models.BooleanField(verbose_name='Yes, I am willing to be a Kitchen Witch/Wizard', default=False),
        ),
        migrations.AlterField(
            model_name='croosupplement',
            name='safety_lead_willing',
            field=models.BooleanField(verbose_name='Yes, I am willing to be a Safety Lead', default=False),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='allergen_information',
            field=models.TextField(blank=True, verbose_name='What happens if you come into contact with this allergen (e.g. I get hives, I go into anaphylactic shock)?'),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='trainings',
            field=models.BooleanField(verbose_name='I understand that if I am accepted as a Crooling or Trip Leader I will be required to get First Aid and CPR training, as well as attend croo and leader specific training. I understand that if I do not meet these requirements, I will not be able to be on a Croo/lead a trip.', default=False),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='trippee_confidentiality',
            field=models.BooleanField(verbose_name="If selected to be a Trips Leader or Crooling, I understand that I will be given access to Trippees' confidential medical information for safety purposes. I pledge to maintain the confidentiality of this information, except as is required by medical or legal concerns", default=False),
        ),
        migrations.AlterField(
            model_name='leadersupplement',
            name='supplement',
            field=models.FileField(blank=True, verbose_name='leader application answers', upload_to=''),
        ),
    ]

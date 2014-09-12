# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0012_auto_20140912_1600'),
    ]

    operations = [
        migrations.RenameField(
            model_name='leaderapplication',
            old_name='answer_from',
            new_name='from_where',
        ),
        migrations.RenameField(
            model_name='leaderapplication',
            old_name='answer_study',
            new_name='what_do_you_like_to_study',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='answer_confidentiality',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='answer_goodstanding',
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='in_goodstanding_with_college',
            field=models.BooleanField(verbose_name='By applying to lead a DOC Trip, I acknowledge that I am in good standing with the College. This may be verified by DOC Trips through the Undergraduate Dean’s Office.', default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='trip_preference_comments',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='trippee_confidentiality',
            field=models.BooleanField(verbose_name="If selected to be a DOC Trips Leader, I understand that I will be given access to my Trippees' confidential medical information for safety purposes. I pledge to maintain the confidentiality of this information, except as is required by medical or legal concerns", default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='offcampus_address',
            field=models.CharField(blank=True, verbose_name='Off-campus address (where can we reach you this summer?', max_length=255),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fyt.applications.models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0002_auto_20150909_2313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalapplication',
            name='in_goodstanding_with_college',
            field=models.BooleanField(verbose_name='By applying to lead a DOC Trip, I acknowledge that I am in good standing with the College. This may be verified by DOC Trips through the Undergraduate Dean’s Office.', validators=[fyt.applications.models.validate_condition_true], default=False),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='trainings',
            field=models.BooleanField(verbose_name='I understand that if I am accepted as a Crooling or Trip Leader I will be required to get First Aid and CPR training, as well as attend croo and leader specific training. I understand that if I do not meet these requirements, I will not be able to be on a Croo/lead a trip.', validators=[fyt.applications.models.validate_condition_true], default=False),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='trippee_confidentiality',
            field=models.BooleanField(verbose_name="If selected to be a Trips Leader or a Croo member, I understand that I will be given access to Trippees' confidential medical information for safety purposes. I pledge to maintain the confidentiality of this information, except as is required by medical or legal concerns", validators=[fyt.applications.models.validate_condition_true], default=False),
        ),
    ]

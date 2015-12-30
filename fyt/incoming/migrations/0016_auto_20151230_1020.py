# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fyt.incoming.models


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0015_incomingstudent_hinman_box'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='_camping_experience',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], verbose_name='Have you ever spent a night camping under a tarp?', default=False),
        ),
        migrations.AddField(
            model_name='registration',
            name='_doc_membership',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], verbose_name='Would you like to purchase a DOC membership?', default=False),
        ),
        migrations.AddField(
            model_name='registration',
            name='_financial_assistance',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], verbose_name="Are you requesting financial assistance from DOC Trips? If 'yes' we will contact you in July with more information about your financial assistance.", default=False),
        ),
        migrations.AddField(
            model_name='registration',
            name='_has_boating_experience',
            field=models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No')], default=None, verbose_name='Have you ever been on an overnight or extended canoe or kayak trip?'),
        ),
        migrations.AddField(
            model_name='registration',
            name='_hiking_experience',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], verbose_name='Have you ever hiked or climbed with a pack of at least 20-30 pounds (10-15 kilograms)?', default=False),
        ),
        migrations.AddField(
            model_name='registration',
            name='_is_exchange',
            field=models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No')], default=None, verbose_name='Are you an Exchange Student?'),
        ),
        migrations.AddField(
            model_name='registration',
            name='_is_fysep',
            field=models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No')], default=None, verbose_name='Are you participating in the First Year Student Enrichment Program (FYSEP)?'),
        ),
        migrations.AddField(
            model_name='registration',
            name='_is_international',
            field=models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No')], default=None, verbose_name='Are you an International Student who plans on attending the International Student Orientation?'),
        ),
        migrations.AddField(
            model_name='registration',
            name='_is_native',
            field=models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No')], default=None, verbose_name='Are you a Native American Student who plans on attending the Native American student orientation?'),
        ),
        migrations.AddField(
            model_name='registration',
            name='_is_transfer',
            field=models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No')], default=None, verbose_name='Are you a Transfer Student?'),
        ),
        migrations.AddField(
            model_name='registration',
            name='_regular_exercise',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], verbose_name='Do you do enjoy cardiovascular exercise (running, biking, swimming, sports, etc.) on a regular basis?', default=False),
        ),
        migrations.AddField(
            model_name='registration',
            name='_waiver',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False, verbose_name='I certify that I have read this assumption of risk and the accompanying registration materials. I approve participation for the student indicated above and this serves as my digital signature of this release, waiver and acknowledgement.', validators=[fyt.incoming.models.validate_waiver]),
        ),
    ]

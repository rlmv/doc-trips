# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('leaders', '0004_auto_20150206_2328'),
    ]

    operations = [
        migrations.RenameField(
            model_name='leaderapplication',
            old_name='is_in_hanover_this_fall',
            new_name='in_hanover_this_fall',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='best_compliment',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='coleader_qualities',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='comforting_experience',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='express_yourself',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='leadership_experience',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='medical_certifications',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='personal_communities',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='relevant_experience',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='tell_us_about_yourself',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='trip_leader_roles',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='what_to_change_about_trips',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='why_do_you_want_to_be_involved',
        ),
        migrations.RemoveField(
            model_name='leaderapplication',
            name='working_with_difference',
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='community_building',
            field=models.DateField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='first_aid',
            field=models.DateField(blank=True, verbose_name='First Aid/CPR', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='risk_management',
            field=models.DateField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='wilderness_skills',
            field=models.DateField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='applicant',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='cannot_participate_in',
            field=models.TextField(blank=True, verbose_name='If applicable, please elaborate (to the extent you feel comfortable) on any particular trips or activities that you absolutely cannot participate in. This information will be used exclusively for trip assignments & co-leader pairings. All information in this application will remain confidential.'),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('WAITLISTED', 'Waitlisted'), ('REJECTED', 'Rejected'), ('CROO', 'Croo'), ('CANCELED', 'Cancelled'), ('DEPRECATED', 'Deprecated'), ('DISQUALIFIED', 'Disqualified')], max_length=15, default='PENDING', verbose_name='Application status'),
        ),
    ]

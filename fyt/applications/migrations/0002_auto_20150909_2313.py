# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db', '0001_initial'),
        ('croos', '0001_initial'),
        ('trips', '0001_initial'),
        ('applications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='skippedleadergrade',
            name='grader',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='skippedleadergrade',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='skippedcroograde',
            name='application',
            field=models.ForeignKey(related_name='skips', to='applications.CrooSupplement', editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='skippedcroograde',
            name='for_qualification',
            field=models.ForeignKey(to='applications.QualificationTag', editable=False, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='skippedcroograde',
            name='grader',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='skippedcroograde',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='qualificationtag',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='portalcontent',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='portalcontent',
            unique_together=set([('trips_year',)]),
        ),
        migrations.AddField(
            model_name='leadersupplement',
            name='application',
            field=models.OneToOneField(related_name='leader_supplement', to='applications.GeneralApplication', editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leadersupplement',
            name='available_sections',
            field=models.ManyToManyField(to='trips.Section', related_name='available_leaders', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leadersupplement',
            name='available_triptypes',
            field=models.ManyToManyField(to='trips.TripType', related_name='available_triptypes', blank=True, verbose_name='Available types of trips'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leadersupplement',
            name='preferred_sections',
            field=models.ManyToManyField(to='trips.Section', related_name='preferred_leaders', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leadersupplement',
            name='preferred_triptypes',
            field=models.ManyToManyField(to='trips.TripType', related_name='preferred_leaders', blank=True, verbose_name='Preferred types of trips'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leadersupplement',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplicationgrade',
            name='application',
            field=models.ForeignKey(related_name='grades', to='applications.LeaderSupplement', editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplicationgrade',
            name='grader',
            field=models.ForeignKey(related_name='leaderapplicationgrades', to=settings.AUTH_USER_MODEL, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplicationgrade',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='applicant',
            field=models.ForeignKey(related_name='applications', to=settings.AUTH_USER_MODEL, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='assigned_croo',
            field=models.ForeignKey(related_name='croo_members', on_delete=django.db.models.deletion.PROTECT, to='croos.Croo', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='assigned_trip',
            field=models.ForeignKey(related_name='leaders', on_delete=django.db.models.deletion.PROTECT, to='trips.Trip', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='generalapplication',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='application',
            field=models.OneToOneField(related_name='croo_supplement', to='applications.GeneralApplication', editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crooapplicationgrade',
            name='application',
            field=models.ForeignKey(related_name='grades', to='applications.CrooSupplement', editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crooapplicationgrade',
            name='grader',
            field=models.ForeignKey(related_name='crooapplicationgrades', to=settings.AUTH_USER_MODEL, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crooapplicationgrade',
            name='qualifications',
            field=models.ManyToManyField(to='applications.QualificationTag', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crooapplicationgrade',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicationinformation',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='applicationinformation',
            unique_together=set([('trips_year',)]),
        ),
    ]

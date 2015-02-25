# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('croos', '0008_auto_20150216_0239'),
        ('db', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trips', '0013_auto_20150204_1628'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrooSupplement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='')),
                ('safety_dork_qualified', models.BooleanField(default=False)),
                ('safety_dork', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeneralApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('class_year', models.PositiveIntegerField()),
                ('gender', models.CharField(max_length=25)),
                ('race_ethnicity', models.CharField(verbose_name='race/ethnicity', max_length=255, blank=True, help_text='optional')),
                ('hinman_box', models.CharField(max_length=10)),
                ('phone', models.CharField(verbose_name='cell phone number', max_length=255, blank=True)),
                ('summer_address', models.CharField(max_length=255, blank=True, help_text="don't worry if you don't know yet")),
                ('tshirt_size', models.CharField(max_length=2, choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra large')])),
                ('from_where', models.CharField(verbose_name='Where are you from?', max_length=255)),
                ('what_do_you_like_to_study', models.CharField(verbose_name='What do you like to study?', max_length=255)),
                ('personal_activities', models.TextField(verbose_name='Please list your primary activities and involvements at Dartmouth and beyond', blank=True)),
                ('feedback', models.TextField(verbose_name='If you have any experience with Trips, what would you change about the program (big or small)?  If you do not have experience with Trips, what would you change about the program OR what would you change about your introduction to Dartmouth?', blank=True)),
                ('dietary_restrictions', models.TextField(verbose_name='Do you have any dietary restrictions or allergies that we should know about?', blank=True)),
                ('allergen_information', models.TextField(verbose_name='What happens if you come into contact with this allergen (e.g. I turn purple and squishy if I eat a grape!)?', blank=True)),
                ('medical_certifications', models.TextField(blank=True)),
                ('medical_experience', models.TextField(verbose_name='Briefly describe your experience with your safety certifications. How frequently do you use your certification and in what circumstances?', blank=True)),
                ('peer_training', models.TextField(verbose_name='If you have participated in or lead a peer training program, such as DPP, IGD, DBI, MAV, EDPA, SAPA, DAPA, UGA, etc. please list them here, and briefly describe them.', blank=True)),
                ('trippee_confidentiality', models.BooleanField(verbose_name="If selected to be a DOC Trips Leader, I understand that I will be given access to my Trippees' confidential medical information for safety purposes. I pledge to maintain the confidentiality of this information, except as is required by medical or legal concerns", default=False)),
                ('in_goodstanding_with_college', models.BooleanField(verbose_name='By applying to lead a DOC Trip, I acknowledge that I am in good standing with the College. This may be verified by DOC Trips through the Undergraduate Dean’s Office.', default=False)),
                ('trainings', models.BooleanField(verbose_name='I understand that if I am accepted as a crooling or trip leader I will be required to get First Aid and CPR training, as well as attend croo and leader specific training. I understand that if I do not meet these requirements, I will not be able to be on a croo/lead a trip.', default=False)),
                ('spring_training_ok', models.BooleanField(verbose_name='I can attend trainings during the spring term.', default=False)),
                ('summer_training_ok', models.BooleanField(verbose_name='I can attend trainings during the summer term.', default=False)),
                ('applicant', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('trips_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LeaderSupplement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='')),
                ('trip_preference_comments', models.TextField(verbose_name='Looking at the Trips descriptions, please feel free to use this space to address any concerns or explain your availability. This will only be used to help us in Trip assignments, it will not be considered when your application is being read.', blank=True)),
                ('cannot_participate_in', models.TextField(verbose_name='If applicable, please elaborate (to the extent you feel comfortable) on any particular trips or activities that you absolutely cannot participate in. This information will be used exclusively for trip assignments & co-leader pairings. All information in this application will remain confidential.', blank=True)),
                ('experience', models.TextField(verbose_name='For each type of trip you are interested in leading, please describe your level of expertise and any amount of previous experience that might qualify you to lead that particular trip (DOC Wilderness Leader, lifeguard training, yoga experience, mountain biking enthusiast, photography class, NOLS, etc.).', blank=True)),
                ('community_building', models.DateField(null=True, blank=True)),
                ('risk_management', models.DateField(null=True, blank=True)),
                ('wilderness_skills', models.DateField(null=True, blank=True)),
                ('first_aid', models.DateField(verbose_name='First Aid/CPR', null=True, blank=True)),
                ('application', models.OneToOneField(to='applications.GeneralApplication')),
                ('available_sections', models.ManyToManyField(to='trips.Section', related_name='available_leaders', blank=True)),
                ('available_triptypes', models.ManyToManyField(verbose_name='Available types of trips', to='trips.TripType', related_name='available_triptypes', blank=True)),
                ('preferred_sections', models.ManyToManyField(to='trips.Section', related_name='preferred_leaders', blank=True)),
                ('preferred_triptypes', models.ManyToManyField(verbose_name='Preferred types of trips', to='trips.TripType', related_name='preferred_leaders', blank=True)),
                ('trips_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='application',
            field=models.OneToOneField(to='applications.GeneralApplication'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='assigned_croo',
            field=models.ForeignKey(related_name='croolings', null=True, to='croos.Croo', blank=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='potential_croos',
            field=models.ManyToManyField(to='croos.Croo', related_name='potential_croolings', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='croosupplement',
            name='trips_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db.TripsYear', editable=False),
            preserve_default=True,
        ),
    ]

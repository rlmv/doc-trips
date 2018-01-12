# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leader_supplement_questions', models.FileField(upload_to='', help_text='.docx file', verbose_name='Leader Application questions')),
                ('croo_supplement_questions', models.FileField(upload_to='', help_text='.docx file', verbose_name='Croo Application questions')),
                ('application_header', models.TextField(blank=True, help_text='This will be displayed at the top of all application pages')),
                ('general_info', models.TextField(blank=True, help_text='This will be displayed at the top of the General Information tab')),
                ('leader_info', models.TextField(blank=True, help_text='This will be displayed at the top of the Leader Application tab')),
                ('croo_info', models.TextField(blank=True, help_text='This will be displayed at the top of Croo Application tab')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrooApplicationGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.PositiveSmallIntegerField(choices=[(1, "1 -- Bad application -- I really don't want this person to be a volunteer and I have serious concerns"), (2, '2 -- Poor application -- I have some concerns about this person being a Trips volunteer'), (3, '3 -- Fine application -- This person might work well as a volunteer but I have some questions'), (4, "4 -- Good application -- I would consider this person to be a volunteer but I wouldn't be heartbroken if they were not selected"), (5, '5 -- Great application -- I think this person would be a fantastic volunteer'), (6, '6 -- Incredible application -- I think this person should be one of the first to be selected to be a volunteer. I would be very frustrated/angry if this person is not selected')], verbose_name='score')),
                ('hard_skills', models.CharField(max_length=255, blank=True)),
                ('soft_skills', models.CharField(max_length=255, blank=True)),
                ('comment', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrooSupplement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='', blank=True, verbose_name='Croo Application Answers')),
                ('safety_lead_willing', models.BooleanField(default=False, verbose_name='Yes, I am willing to be a Safety Lead')),
                ('kitchen_lead_willing', models.BooleanField(default=False, verbose_name='Yes, I am willing to be a Kitchen Witch/Wizard')),
                ('kitchen_lead_qualifications', models.TextField(help_text='(eg. on Moosilauke Lodge crew spring 2014, experience working in industrial kitchens, experience preparing and organizing food for large groups)', verbose_name='If you are willing to be a Kitchen Witch/Wizard, please briefly describe your qualifications for the position')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeneralApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=15, choices=[('PENDING', 'Pending'), ('CROO', 'Croo'), ('LEADER', 'Leader'), ('LEADER_WAITLIST', 'Leader Waitlist'), ('REJECTED', 'Rejected'), ('CANCELED', 'Canceled')], default='PENDING', verbose_name='Application status')),
                ('safety_lead', models.BooleanField(default=False)),
                ('community_building', models.DateField(null=True, blank=True)),
                ('risk_management', models.DateField(null=True, blank=True)),
                ('wilderness_skills', models.DateField(null=True, blank=True)),
                ('croo_training', models.DateField(null=True, blank=True)),
                ('fa_cert', models.CharField(default='', max_length=10, choices=[(None, '--'), ('FA', 'First Aid'), ('CPR', 'CPR'), ('FA/CPR', 'First Aid/CPR'), ('WFA', 'WFA'), ('WFR', 'WFR'), ('W-EMT', 'W-EMT'), ('EMT', 'EMT'), ('OEC', 'OEC'), ('other', 'other')], blank=True, verbose_name='first aid cert')),
                ('fa_other', models.CharField(default='', max_length=100, blank=True, verbose_name='other first aid cert')),
                ('class_year', models.PositiveIntegerField()),
                ('gender', models.CharField(max_length=25)),
                ('race_ethnicity', models.CharField(max_length=255, help_text='optional', blank=True, verbose_name='race/ethnicity')),
                ('hinman_box', models.CharField(max_length=10)),
                ('phone', models.CharField(max_length=255, blank=True, verbose_name='cell phone number')),
                ('summer_address', models.CharField(max_length=255, blank=True, help_text="don't worry if you don't know yet")),
                ('tshirt_size', models.CharField(max_length=2, choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra large')])),
                ('from_where', models.CharField(max_length=255, verbose_name='Where are you from?')),
                ('what_do_you_like_to_study', models.CharField(max_length=255, verbose_name='What do you like to study?')),
                ('personal_activities', models.TextField(blank=True, verbose_name='In order of importance to you, please list your activities and involvements at Dartmouth and beyond (e.g. greek affiliation, affinity group, campus organization, team, etc)')),
                ('feedback', models.TextField(blank=True, verbose_name='If you have any experience with Trips, what would you change about the program (big or small)?  If you do not have experience with Trips, what would you change about the program OR what would you change about your introduction to Dartmouth?')),
                ('hanover_in_fall', models.CharField(max_length=5, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Are you planning to be in Hanover this fall?')),
                ('role_preference', models.CharField(max_length=20, choices=[('PREFER_LEADER', 'Prefer Trip Leader'), ('PREFER_CROO', 'Prefer Croo'), ('N/A', 'N/A')], default='N/A', verbose_name="While Trips Directorate will ultimately decide where we think you will be most successful in the program, we would like to know your preferences. If you are submitting a Trip Leader application AND a Croo application, please indicate which position you prefer. If you are only applying to one position, please choose 'N/A'")),
                ('dietary_restrictions', models.TextField(blank=True, verbose_name='Do you have any dietary restrictions or allergies that we should know about?')),
                ('allergen_information', models.TextField(blank=True, verbose_name='What happens if you come into contact with this allergen (e.g. I get hives, I go into anaphylactic shock)?')),
                ('medical_certifications', models.TextField(help_text="eg. 'First Aid - American Red Cross, expires October 2013.'", blank=True, verbose_name='Current trainings in First Aid and CPR are required for all DOC trip leaders and croo members. Please list any relevant medical certifications you hold (e.g. First Aid, CPR, Wilderness First Aid, Wilderness First Responder, Emergency Medical Technician, Wilderness Emergency Medical Technician, Outdoor Emergency Care). Also list the program that sponsored the certification, and the dates they expire. If you do not currently have such a certification (or if your certification will expire before Trips ends), we will be in touch about how you can get trained through Trips-sponsored First Aid & CPR courses in the spring and summer.')),
                ('medical_experience', models.TextField(blank=True, verbose_name='Briefly describe your experience with your safety certifications. How frequently do you use your certification and in what circumstances?')),
                ('peer_training', models.TextField(blank=True, verbose_name='List and briefly describe any peer training program (DPP, IGD, DBI, MAV, EDPA, SAPA, DAPA, UGA, etc.) that you have lead or participated in.')),
                ('trippee_confidentiality', models.BooleanField(default=False, verbose_name="If selected to be a Trips Leader or a Croo member, I understand that I will be given access to Trippees' confidential medical information for safety purposes. I pledge to maintain the confidentiality of this information, except as is required by medical or legal concerns")),
                ('in_goodstanding_with_college', models.BooleanField(default=False, verbose_name='By applying to lead a DOC Trip, I acknowledge that I am in good standing with the College. This may be verified by DOC Trips through the Undergraduate Dean’s Office.')),
                ('trainings', models.BooleanField(default=False, verbose_name='I understand that if I am accepted as a Crooling or Trip Leader I will be required to get First Aid and CPR training, as well as attend croo and leader specific training. I understand that if I do not meet these requirements, I will not be able to be on a Croo/lead a trip.')),
                ('spring_training_ok', models.BooleanField(default=False, verbose_name='I can attend trainings during the spring term.')),
                ('summer_training_ok', models.BooleanField(default=False, verbose_name='I can attend trainings during the summer term.')),
            ],
            options={
                'ordering': ['applicant'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LeaderApplicationGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.PositiveSmallIntegerField(choices=[(1, "1 -- Bad application -- I really don't want this person to be a volunteer and I have serious concerns"), (2, '2 -- Poor application -- I have some concerns about this person being a Trips volunteer'), (3, '3 -- Fine application -- This person might work well as a volunteer but I have some questions'), (4, "4 -- Good application -- I would consider this person to be a volunteer but I wouldn't be heartbroken if they were not selected"), (5, '5 -- Great application -- I think this person would be a fantastic volunteer'), (6, '6 -- Incredible application -- I think this person should be one of the first to be selected to be a volunteer. I would be very frustrated/angry if this person is not selected')], verbose_name='score')),
                ('hard_skills', models.CharField(max_length=255, blank=True)),
                ('soft_skills', models.CharField(max_length=255, blank=True)),
                ('comment', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LeaderSupplement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='', verbose_name='leader application answers', blank=True, db_index=True)),
                ('trip_preference_comments', models.TextField(blank=True, verbose_name='Looking at the Trips descriptions, please feel free to use this space to address any concerns or explain your availability. This will only be used to help us in Trip assignments, it will not be considered when your application is being read.')),
                ('cannot_participate_in', models.TextField(blank=True, verbose_name='If applicable, please elaborate (to the extent you feel comfortable) on any particular trips or activities that you absolutely cannot participate in. This information will be used exclusively for trip assignments & co-leader pairings. All information in this application will remain confidential.')),
                ('relevant_experience', models.TextField(blank=True, verbose_name='For each type of trip you are interested in leading, please describe your level of expertise and any amount of previous experience that might qualify you to lead that particular trip (DOC Wilderness Leader, lifeguard training, yoga experience, mountain biking enthusiast, photography class, NOLS, etc.).')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PortalContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PENDING_description', models.TextField(blank=True)),
                ('CROO_description', models.TextField(blank=True)),
                ('LEADER_description', models.TextField(blank=True)),
                ('LEADER_WAITLIST_description', models.TextField(blank=True)),
                ('REJECTED_description', models.TextField(blank=True)),
                ('CANCELED_description', models.TextField(blank=True)),
                ('day0_description', models.TextField(help_text="description for leaders' first day, Gilman Island, etc.", blank=True, verbose_name='day 0 description')),
                ('day1_description', models.TextField(help_text='post-Gilman, trippee arrival, swim test, safety talk, etc.', blank=True, verbose_name='day 1 description')),
                ('day5_description', models.TextField(help_text='return to campust, pre-o', blank=True, verbose_name='day 5 description')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QualificationTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='I think this applicant is qualified for the following roles:')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SkippedCrooGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SkippedLeaderGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application', models.ForeignKey(related_name='skips', to='applications.LeaderSupplement', editable=False, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]

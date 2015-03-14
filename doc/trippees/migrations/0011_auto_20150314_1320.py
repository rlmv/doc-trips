# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0017_auto_20150310_1431'),
        ('transport', '0016_auto_20150204_1628'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db', '__first__'),
        ('trippees', '0010_collegeinfo_class_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomingStudent',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('decline_reason', models.CharField(max_length=50, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('name', models.CharField(max_length=255)),
                ('netid', models.CharField(max_length=20)),
                ('class_year', models.CharField(max_length=10)),
                ('ethnic_code', models.CharField(max_length=1)),
                ('gender', models.CharField(max_length=10)),
                ('incoming_status', models.CharField(max_length=20, choices=[('EXCHANGE', 'Exchange'), ('TRANSFER', 'Transfer'), ('FIRSTYEAR', 'First Year')])),
                ('email', models.EmailField(max_length=254)),
                ('dartmouth_email', models.EmailField(max_length=254)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('gender', models.CharField(max_length=50)),
                ('previous_school', models.CharField(max_length=255, verbose_name='high school, or most recent school')),
                ('home_phone', models.CharField(max_length=20)),
                ('cell_phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('guardian_email', models.EmailField(max_length=254, verbose_name='parent/guardian email')),
                ('schedule_conflicts', models.TextField(blank=True)),
                ('tshirt_size', models.CharField(max_length=2, choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra large')])),
                ('medical_conditions', models.TextField(verbose_name='Do you have any medical conditions, past injuries, disabilities or allergies that we should be aware of? Please describe any injury, condition, disability, or illness which we should take into consideration in assigning you to a trip')),
                ('allergies', models.TextField(verbose_name='Please describe any allergies you have (e.g. bee stings, specific medications, foods, etc.) which might require special medical attention.')),
                ('allergen_information', models.TextField(verbose_name='What happens if you come into contact with this allergen (e.g. I get hives, I go into anaphylactic shock)?')),
                ('needs', models.TextField(verbose_name='While many students manage their own health needs, we would prefer that you let us know of any other needs or conditions so we can ensure your safety and comfort during the trip.')),
                ('dietary_restrictions', models.TextField(verbose_name='Do you have any dietary restrictions we should be aware of (vegetarian, gluten-free, etc.)? We can accommodate ANY and ALL dietary needs as long as we know in advance. Leave blank if not applicable')),
                ('regular_exercise', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')])),
                ('physical_activities', models.TextField(verbose_name='Please describe the types of physical activities you enjoy, including frequency (daily? weekly?) and extent (number of miles or hours)')),
                ('other_activities', models.TextField(verbose_name='Do you do any other activities that might assist us in assign you to a trip (yoga, karate, horseback riding, photography, fishing, etc.)?')),
                ('summer_plans', models.TextField(verbose_name='Please describe your plans for the summer (working at home, volunteering, etc.)')),
                ('swimming_ability', models.CharField(max_length=20, choices=[('NON_SWIMMER', 'Non-Swimmer'), ('BEGINNER', 'Beginner'), ('COMPETENT', 'Competent'), ('EXPERT', 'Expert')])),
                ('camping_experience', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Have you ever spent a night camping in the outdoors?')),
                ('hiking_experience', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Have you ever hiked or climbed with a pack of at least 20-30 pounds (10-15 kilograms)?')),
                ('hiking_experience_description', models.TextField(verbose_name='Please describe your hiking experience. Where have you hiked? Was it mountainous or flat? Have you done day hikes? Have you hiked while carrying food and shelter with you? Please be specific: we want to physically challenge you as little or as much as you want. Be honest so that we can place you on the right trip for YOU. If you have questions about this, please let us know.', blank=True)),
                ('has_boating_experience', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Have you ever been on an overnight or extended canoe or kayak trip?')),
                ('boating_experience', models.TextField(verbose_name='Please describe your canoe or kayak trip experience. Have you paddled on flat water? Have you paddled on flat water? When did you do these trips and how long were they?')),
                ('other_boating_experience', models.TextField(verbose_name='Please describe any other paddling experience you have had. Be specific regarding location, type of water, and distance covered.')),
                ('fishing_experience', models.TextField(verbose_name='Please describe your fishing experience.')),
                ('horseback_riding_experience', models.TextField(verbose_name='Please describe your riding experience and ability level. What riding styles are you familiar with? How recently have you ridden horses on a regular basis? NOTE: Prior exposure and some experience is preferred for this trip.')),
                ('mountain_biking_experience', models.TextField(verbose_name='Please describe your biking experience and ability level. Have you done any biking off of paved trails? How comfortable are you riding on dirt and rocks?')),
                ('anything_else', models.TextField(verbose_name="Is there any other information you'd like to provide (anything helps!) that would assist us in assigning you to a trip?")),
                ('financial_assistance', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name="Are you requesting financial assistance from DOC Trips? If 'yes' we will contact you in July with more information about your financial assistance.")),
                ('waiver', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='I certify that I have read this assumption of risk and the accompanying registration materials. I approve participation for the student indicated above and this serves as my digital signature of this release, waiver & acknowledgement.')),
                ('doc_membership', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')])),
                ('green_fund_donation', models.PositiveSmallIntegerField()),
                ('final_request', models.TextField(verbose_name='We know this form is really long, so thanks for sticking with us! The following question has nothing to do with your trip assignment. To whatever extent you feel comfortable, please share one thing you are excited and/or nervous for about coming to Dartmouth (big or small). There is no right or wrong answers - anything goes! All responses will be remain anonymous.')),
                ('bus_stop', models.ForeignKey(to='transport.Stop', verbose_name='Where would you like to be bussed from/to?', on_delete=django.db.models.deletion.PROTECT)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False, on_delete=django.db.models.deletion.PROTECT)),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='collegeinfo',
            name='trips_year',
        ),
        migrations.RemoveField(
            model_name='trippee',
            name='info',
        ),
        migrations.DeleteModel(
            name='CollegeInfo',
        ),
        migrations.RemoveField(
            model_name='trippee',
            name='registration',
        ),
        migrations.RemoveField(
            model_name='trippee',
            name='trip_assignment',
        ),
        migrations.RemoveField(
            model_name='trippee',
            name='trips_year',
        ),
        migrations.DeleteModel(
            name='Trippee',
        ),
        migrations.RemoveField(
            model_name='trippeeregistration',
            name='bus_stop',
        ),
        migrations.RemoveField(
            model_name='trippeeregistration',
            name='trips_year',
        ),
        migrations.RemoveField(
            model_name='trippeeregistration',
            name='user',
        ),
        migrations.DeleteModel(
            name='TrippeeRegistration',
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='registration',
            field=models.OneToOneField(editable=False, to='trippees.Registration', related_name='trippee', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='trip_assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='trips.ScheduledTrip', related_name='trippees', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False, on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
    ]

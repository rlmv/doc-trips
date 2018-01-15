# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fyt.users.models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomingStudent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cancelled', models.BooleanField(default=False, help_text='this Trippee will still be charged even though they are no longer going on a trip', verbose_name='cancelled last-minute?')),
                ('financial_aid', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='percentage financial assistance')),
                ('med_info', models.TextField(blank=True, help_text='Use this field for additional medical info not provided in the registration, or simplified information if some details do not need to be provided to leaders and croos.')),
                ('show_med_info', models.BooleanField(default=False, help_text="Medical information in this trippee's registration will be displayed in leader and croo packets. (This information is hidden by default.)", verbose_name='Show registration med info?')),
                ('decline_reason', models.CharField(max_length=50, blank=True)),
                ('notes', models.TextField(blank=True, help_text='These notes are displayed to the trippee along with their trip assignment.')),
                ('name', models.CharField(max_length=512)),
                ('netid', fyt.users.models.NetIdField(max_length=20)),
                ('class_year', models.CharField(max_length=10)),
                ('ethnic_code', models.CharField(max_length=100)),
                ('gender', models.CharField(max_length=100)),
                ('birthday', models.CharField(max_length=20)),
                ('incoming_status', models.CharField(max_length=20, blank=True, choices=[('EXCHANGE', 'Exchange'), ('TRANSFER', 'Transfer'), ('FIRSTYEAR', 'First Year')])),
                ('email', models.EmailField(max_length=254)),
                ('blitz', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=30)),
                ('address', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('gender', models.CharField(max_length=50)),
                ('previous_school', models.CharField(max_length=255, verbose_name='high school, or most recent school')),
                ('phone', models.CharField(max_length=20, verbose_name='phone number')),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('guardian_email', models.EmailField(max_length=254, blank=True, verbose_name='parent/guardian email')),
                ('is_exchange', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], blank=True, verbose_name='Are you an Exchange Student?')),
                ('is_transfer', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], blank=True, verbose_name='Are you a Transfer Student?')),
                ('is_international', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], blank=True, verbose_name='Are you an International Student who plans on attending the International Student Orientation?')),
                ('is_native', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], blank=True, verbose_name='Are you a Native American Student who plans on attending the Native American student orientation?')),
                ('is_fysep', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], blank=True, verbose_name='Are you participating in the First Year Student Enrichment Program (FYSEP)?')),
                ('is_athlete', models.CharField(max_length=100, choices=[('NO', 'No'), ('ALPINE_SKIING', 'Alpine Skiing'), ('FOOTBALL', 'Football'), ('MENS_SOCCER', "Men's Soccer"), ('WOMENS_SOCCER', "Women's Soccer"), ('FIELD_HOCKEY', 'Field Hockey'), ('VOLLEYBALL', 'Volleyball'), ('MENS_HEAVYWEIGHT_CREW', "Men's Heavyweight Crew"), ('MENS_LIGHTWEIGHT_CREW', "Men's Lightweight Crew"), ('WOMENS_CREW', "Women's Crew"), ('MENS_CROSS_COUNTRY', "Men's Cross Country"), ('WOMENS_CROSS_COUNTRY', "Women's Cross Country"), ('MENS_GOLF', "Men's Golf"), ('WOMENS_GOLF', "Women's Golf"), ('MENS_TENNIS', "Men's Tennis"), ('WOMENS_TENNIS', "Women's Tennis"), ('MENS_RUGBY', "Men's Rugby"), ('WOMENS_RUGBY', "Women's Rugby"), ('SAILING', 'Sailing'), ('MENS_WATER_POLO', "Men's Water Polo")], help_text="Each team has its own pre-season schedule. We are in close contact with fall coaches and will assign you to a trip section that works well for the team's pre-season schedule.", blank=True, verbose_name='Are you a Fall varsity athlete (or Rugby or Water Polo)?')),
                ('schedule_conflicts', models.TextField(blank=True)),
                ('tshirt_size', models.CharField(max_length=2, choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra large')])),
                ('medical_conditions', models.TextField(blank=True, verbose_name='Do you have any medical conditions, past injuries, disabilities or allergies that we should be aware of? Please describe any injury, condition, disability, or illness which we should take into consideration in assigning you to a trip')),
                ('allergies', models.TextField(blank=True, verbose_name='Please describe any allergies you have (e.g. bee stings, specific medications, foods, etc.) which might require special medical attention.')),
                ('allergen_information', models.TextField(blank=True, verbose_name='What happens if you come into contact with this allergen (e.g. I get hives, I go into anaphylactic shock)?')),
                ('epipen', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], blank=True, verbose_name='Do you carry an EpiPen? If yes, please bring it with you on Trips.')),
                ('needs', models.TextField(blank=True, verbose_name='While many students manage their own health needs, we would prefer that you let us know of any other needs or conditions so we can ensure your safety and comfort during the trip (e.g. Diabetes, recent surgery, migraines).')),
                ('dietary_restrictions', models.TextField(blank=True, verbose_name='Do you have any dietary restrictions we should be aware of (vegetarian, gluten-free, etc.)? We can accommodate ANY and ALL dietary needs as long as we know in advance. Leave blank if not applicable')),
                ('allergy_severity', models.PositiveIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], null=True, blank=True, verbose_name='If you have a food allergy, please rate the severity of the allergy on a scale from 1 to 5 (1 = itchy skin, puffy eyes and 5 = anaphylaxis).')),
                ('allergy_reaction', models.TextField(blank=True, verbose_name='If you have a food allergy, please describe what happens when you come into contact with the allergen (e.g. I get hives, I go into anaphylactic shock).')),
                ('regular_exercise', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Do you do enjoy cardiovascular exercise (running, biking, swimming, sports, etc.) on a regular basis?')),
                ('physical_activities', models.TextField(blank=True, verbose_name='Please describe the types of physical activities you enjoy, including frequency (daily? weekly?) and extent (number of miles or hours)')),
                ('other_activities', models.TextField(blank=True, verbose_name='Do you do any other activities that might assist us in assigning you to a trip (yoga, karate, horseback riding, photography, fishing, etc.)?')),
                ('swimming_ability', models.CharField(max_length=20, choices=[('NON_SWIMMER', 'Non-Swimmer'), ('BEGINNER', 'Beginner'), ('COMPETENT', 'Competent'), ('EXPERT', 'Expert')], verbose_name='Please rate yourself as a swimmer')),
                ('camping_experience', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Have you ever spent a night camping under a tarp?')),
                ('hiking_experience', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Have you ever hiked or climbed with a pack of at least 20-30 pounds (10-15 kilograms)?')),
                ('hiking_experience_description', models.TextField(blank=True, verbose_name='Please describe your hiking experience. Where have you hiked? Was it mountainous or flat? Have you done day hikes? Have you hiked while carrying food and shelter with you? Please be specific: we want to physically challenge you as little or as much as you want. Be honest so that we can place you on the right trip for YOU. If you have questions about this, please let us know.')),
                ('has_boating_experience', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], blank=True, verbose_name='Have you ever been on an overnight or extended canoe or kayak trip?')),
                ('boating_experience', models.TextField(blank=True, verbose_name='Please describe your canoe or kayak trip experience. Have you paddled on flat water? Have you paddled on flat water? When did you do these trips and how long were they?')),
                ('other_boating_experience', models.TextField(blank=True, verbose_name='Please describe any other paddling experience you have had. Be specific regarding location, type of water, and distance covered.')),
                ('fishing_experience', models.TextField(blank=True, verbose_name='Please describe your fishing experience.')),
                ('horseback_riding_experience', models.TextField(blank=True, verbose_name='Please describe your riding experience and ability level. What riding styles are you familiar with? How recently have you ridden horses on a regular basis? NOTE: Prior exposure and some experience is preferred for this trip.')),
                ('mountain_biking_experience', models.TextField(blank=True, verbose_name='Please describe your biking experience and ability level. Have you done any biking off of paved trails? How comfortable are you riding on dirt and rocks?')),
                ('sailing_experience', models.TextField(blank=True, verbose_name='Please describe your sailing experience.')),
                ('anything_else', models.TextField(blank=True, verbose_name="Is there any other information you'd like to provide (anything helps!) that would assist us in assigning you to a trip?")),
                ('financial_assistance', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name="Are you requesting financial assistance from DOC Trips? If 'yes' we will contact you in July with more information about your financial assistance.")),
                ('waiver', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='I certify that I have read this assumption of risk and the accompanying registration materials. I approve participation for the student indicated above and this serves as my digital signature of this release, waiver and acknowledgement.')),
                ('doc_membership', models.CharField(max_length=3, choices=[('YES', 'yes'), ('NO', 'no')], verbose_name='Would you like to purchase a DOC membership?')),
                ('green_fund_donation', models.PositiveSmallIntegerField(default=0)),
                ('final_request', models.TextField(blank=True, verbose_name='We know this form is really long, so thanks for sticking with us! The following question has nothing to do with your trip assignment. To whatever extent you feel comfortable, please share one thing you are excited and/or nervous for about coming to Dartmouth (big or small). There is no right or wrong answers &mdash; anything goes! All responses will remain anonymous.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trips_cost', models.PositiveSmallIntegerField()),
                ('doc_membership_cost', models.PositiveSmallIntegerField()),
                ('contact_url', models.URLField(help_text='url of trips directorate contact info')),
                ('trips_year', models.ForeignKey(to='core.TripsYear', on_delete=django.db.models.deletion.PROTECT, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='settings',
            unique_together=set([('trips_year',)]),
        ),
    ]

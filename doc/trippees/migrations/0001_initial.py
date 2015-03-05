# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0016_auto_20150204_1628'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrippeeRegistration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
                ('camping_experience', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')])),
                ('hiking_experience', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')])),
                ('hiking_experience_description', models.TextField(blank=True, verbose_name='Please describe your hiking experience. Where have you hiked? Was it mountainous or flat? Have you done day hikes? Have you hiked while carrying food and shelter with you? Please be specific: we want to physically challenge you as little or as much as you want. Be honest so that we can place you on the right trip for YOU. If you have questions about this, please let us know.')),
                ('has_boating_experience', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')])),
                ('boating_experience', models.TextField(verbose_name='Please describe your canoe or kayak trip experience. Have you paddled on flat water? Have you paddled on flat water? When did you do these trips and how long were they?')),
                ('other_boating_experience', models.TextField(verbose_name='Please describe any other paddling experience you have had. Be specific regarding location, type of water, and distance covered.')),
                ('fishing_experience', models.TextField(verbose_name='Please describe your fishing experience.')),
                ('horseback_riding_experience', models.TextField(verbose_name='Please describe your riding experience and ability level. What riding styles are you familiar with? How recently have you ridden horses on a regular basis? NOTE: Prior exposure and some experience is preferred for this trip.')),
                ('mountain_biking_experience', models.TextField(verbose_name='Please describe your biking experience and ability level. Have you done any biking off of paved trails? How comfortable are you riding on dirt and rocks?')),
                ('anything_else', models.TextField(verbose_name="Is there any other information you'd like to provide (anything helps!) that would assist us in assigning you to a trip?")),
                ('financial_assistance', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')])),
                ('waiver', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')])),
                ('doc_membership', models.CharField(max_length=2, choices=[('YES', 'yes'), ('NO', 'no')])),
                ('green_fund_donation', models.PositiveSmallIntegerField()),
                ('final_request', models.TextField(verbose_name='We know this form is really long, so thanks for sticking with us! The following question has nothing to do with your trip assignment. To whatever extent you feel comfortable, please share one thing you are excited and/or nervous for about coming to Dartmouth (big or small). There is no right or wrong answers - anything goes! All responses will be remain anonymous.')),
                ('bus_stop', models.ForeignKey(verbose_name='Where would you like to be bussed from/to?', to='transport.Stop')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators
import django.db.models.deletion
import doc.users.models


def lowercase_netids(apps, schema_editor):

    Registration = apps.get_model('incoming', 'Registration')
    IncomingStudent = apps.get_model('incoming', 'IncomingStudent')
    for student in IncomingStudent.objects.all():
        student.netid = student.netid.lower()
        print('lowercasing incoming student %s %s' % (student, student.netid))
        try:
            student.registration = Registration.objects.get(user__netid=student.netid,
                                                            trips_year=student.trips_year)
            print('linking student %s to registration %s' % (student, student.registration))
        except Registration.DoesNotExist:
            pass
        student.save()


def null_to_zero(apps, schema_editor):

    Registration = apps.get_model('incoming', 'Registration')
    for reg in Registration.objects.all():
        if reg.green_fund_donation is None:
            print('changing %s' % reg)
            reg.green_fund_donation = 0
            reg.save()


class Migration(migrations.Migration):

    replaces = [('incoming', '0001_initial'), ('incoming', '0002_auto_20150305_1852'), ('incoming', '0003_auto_20150310_1551'), ('incoming', '0004_auto_20150310_1619'), ('incoming', '0005_auto_20150311_1234'), ('incoming', '0006_auto_20150311_1336'), ('incoming', '0007_auto_20150312_1031'), ('incoming', '0008_auto_20150312_1142'), ('incoming', '0009_auto_20150313_1249'), ('incoming', '0010_collegeinfo_class_year'), ('incoming', '0011_auto_20150314_1320'), ('incoming', '0012_auto_20150314_1530'), ('incoming', '0013_auto_20150320_1510'), ('incoming', '0014_auto_20150320_1643'), ('incoming', '0015_auto_20150320_1814'), ('incoming', '0016_auto_20150320_1843'), ('incoming', '0017_auto_20150320_1851'), ('incoming', '0018_auto_20150320_1853'), ('incoming', '0019_auto_20150321_1238'), ('incoming', '0020_auto_20150321_1246'), ('incoming', '0021_auto_20150321_1353'), ('incoming', '0022_auto_20150324_1801'), ('incoming', '0023_auto_20150325_1118'), ('incoming', '0024_registration_firstchoice_triptype'), ('incoming', '0025_auto_20150330_1434'), ('incoming', '0026_auto_20150330_1437'), ('incoming', '0027_auto_20150518_1154'), ('incoming', '0028_auto_20150518_1159'), ('incoming', '0029_remove_registration_summer_plans'), ('incoming', '0030_auto_20150518_1251'), ('incoming', '0031_auto_20150519_1130'), ('incoming', '0032_auto_20150519_1132'), ('incoming', '0033_auto_20150519_1703'), ('incoming', '0034_auto_20150527_0024'), ('incoming', '0035_auto_20150527_0034'), ('incoming', '0036_auto_20150527_1402'), ('incoming', '0037_auto_20150531_1411'), ('incoming', '0038_auto_20150531_1413'), ('incoming', '0039_delete_address'), ('incoming', '0040_incomingstudent_bus_assignment'), ('incoming', '0041_auto_20150624_1428'), ('incoming', '0042_incomingstudent_financial_aid'), ('incoming', '0043_auto_20150629_1504'), ('incoming', '0044_auto_20150629_1505'), ('incoming', '0045_auto_20150630_1418'), ('incoming', '0046_auto_20150630_1428'), ('incoming', '0047_auto_20150713_1319'), ('incoming', '0048_auto_20150806_1035'), ('incoming', '0049_auto_20150806_1050')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0006_auto_20150531_1425'),
        ('trips', '0017_auto_20150310_1431'),
        ('transport', '0025_externaltransport'),
        ('db', '__first__'),
        ('trips', '0015_auto_20150224_2104'),
        ('transport', '0016_auto_20150204_1628'),
        ('trips', '0030_rename_ScheduledTrip_to_Trip'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IncomingStudent',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('gender', models.CharField(max_length=50)),
                ('previous_school', models.CharField(max_length=255, verbose_name='high school, or most recent school')),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('guardian_email', models.EmailField(max_length=254, verbose_name='parent/guardian email', blank=True)),
                ('schedule_conflicts', models.TextField(blank=True)),
                ('tshirt_size', models.CharField(max_length=2, choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra large')])),
                ('medical_conditions', models.TextField(verbose_name='Do you have any medical conditions, past injuries, disabilities or allergies that we should be aware of? Please describe any injury, condition, disability, or illness which we should take into consideration in assigning you to a trip', blank=True)),
                ('allergies', models.TextField(verbose_name='Please describe any allergies you have (e.g. bee stings, specific medications, foods, etc.) which might require special medical attention.', blank=True)),
                ('allergen_information', models.TextField(verbose_name='What happens if you come into contact with this allergen (e.g. I get hives, I go into anaphylactic shock)?', blank=True)),
                ('needs', models.TextField(verbose_name='While many students manage their own health needs, we would prefer that you let us know of any other needs or conditions so we can ensure your safety and comfort during the trip (e.g. Diabetes, recent surgery, migraines).', blank=True)),
                ('dietary_restrictions', models.TextField(verbose_name='Do you have any dietary restrictions we should be aware of (vegetarian, gluten-free, etc.)? We can accommodate ANY and ALL dietary needs as long as we know in advance. Leave blank if not applicable', blank=True)),
                ('regular_exercise', models.CharField(max_length=3, verbose_name='Do you do enjoy cardiovascular exercise (running, biking, swimming, sports, etc.) on a regular basis?', choices=[('YES', 'yes'), ('NO', 'no')])),
                ('physical_activities', models.TextField(verbose_name='Please describe the types of physical activities you enjoy, including frequency (daily? weekly?) and extent (number of miles or hours)', blank=True)),
                ('other_activities', models.TextField(verbose_name='Do you do any other activities that might assist us in assigning you to a trip (yoga, karate, horseback riding, photography, fishing, etc.)?', blank=True)),
                ('swimming_ability', models.CharField(max_length=20, verbose_name='Please rate yourself as a swimmer', choices=[('NON_SWIMMER', 'Non-Swimmer'), ('BEGINNER', 'Beginner'), ('COMPETENT', 'Competent'), ('EXPERT', 'Expert')])),
                ('camping_experience', models.CharField(max_length=3, verbose_name='Have you ever spent a night camping under a tarp?', choices=[('YES', 'yes'), ('NO', 'no')])),
                ('hiking_experience', models.CharField(max_length=3, verbose_name='Have you ever hiked or climbed with a pack of at least 20-30 pounds (10-15 kilograms)?', choices=[('YES', 'yes'), ('NO', 'no')])),
                ('hiking_experience_description', models.TextField(verbose_name='Please describe your hiking experience. Where have you hiked? Was it mountainous or flat? Have you done day hikes? Have you hiked while carrying food and shelter with you? Please be specific: we want to physically challenge you as little or as much as you want. Be honest so that we can place you on the right trip for YOU. If you have questions about this, please let us know.', blank=True)),
                ('has_boating_experience', models.CharField(max_length=3, verbose_name='Have you ever been on an overnight or extended canoe or kayak trip?', choices=[('YES', 'yes'), ('NO', 'no')], blank=True)),
                ('boating_experience', models.TextField(verbose_name='Please describe your canoe or kayak trip experience. Have you paddled on flat water? Have you paddled on flat water? When did you do these trips and how long were they?', blank=True)),
                ('other_boating_experience', models.TextField(verbose_name='Please describe any other paddling experience you have had. Be specific regarding location, type of water, and distance covered.', blank=True)),
                ('fishing_experience', models.TextField(verbose_name='Please describe your fishing experience.', blank=True)),
                ('horseback_riding_experience', models.TextField(verbose_name='Please describe your riding experience and ability level. What riding styles are you familiar with? How recently have you ridden horses on a regular basis? NOTE: Prior exposure and some experience is preferred for this trip.', blank=True)),
                ('mountain_biking_experience', models.TextField(verbose_name='Please describe your biking experience and ability level. Have you done any biking off of paved trails? How comfortable are you riding on dirt and rocks?', blank=True)),
                ('anything_else', models.TextField(verbose_name="Is there any other information you'd like to provide (anything helps!) that would assist us in assigning you to a trip?", blank=True)),
                ('financial_assistance', models.CharField(max_length=3, verbose_name="Are you requesting financial assistance from DOC Trips? If 'yes' we will contact you in July with more information about your financial assistance.", choices=[('YES', 'yes'), ('NO', 'no')])),
                ('waiver', models.CharField(max_length=3, verbose_name='I certify that I have read this assumption of risk and the accompanying registration materials. I approve participation for the student indicated above and this serves as my digital signature of this release, waiver and acknowledgement.', choices=[('YES', 'yes'), ('NO', 'no')])),
                ('doc_membership', models.CharField(max_length=3, verbose_name='Would you like to purchase a DOC membership?', choices=[('YES', 'yes'), ('NO', 'no')])),
                ('green_fund_donation', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('final_request', models.TextField(verbose_name='We know this form is really long, so thanks for sticking with us! The following question has nothing to do with your trip assignment. To whatever extent you feel comfortable, please share one thing you are excited and/or nervous for about coming to Dartmouth (big or small). There is no right or wrong answers &mdash; anything goes! All responses will remain anonymous.', blank=True)),
                ('bus_stop', models.ForeignKey(to='transport.Stop', verbose_name='Where would you like to be bussed from/to?', on_delete=django.db.models.deletion.PROTECT, null=True, blank=True)),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False, on_delete=django.db.models.deletion.PROTECT)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False)),
                ('is_athlete', models.CharField(max_length=100, verbose_name='Are you a Fall varsity athlete (or Rugby or Water Polo)?', blank=True, help_text="Each team has its own pre-season schedule. We are in close contact with fall coaches and will assign you to a trip section that works well for the team's pre-season schedule.", choices=[('NO', 'No'), ('ALPINE_SKIING', 'Alpine Skiing'), ('FOOTBALL', 'Football'), ('MENS_SOCCER', "Men's Soccer"), ('WOMENS_SOCCER', "Women's Soccer"), ('FIELD_HOCKEY', 'Field Hockey'), ('VOLLEYBALL', 'Volleyball'), ('MENS_HEAVYWEIGHT_CREW', "Men's Heavyweight Crew"), ('MENS_LIGHTWEIGHT_CREW', "Men's Lightweight Crew"), ('WOMENS_CREW', "Women's Crew"), ('MENS_CROSS_COUNTRY', "Men's Cross Country"), ('WOMENS_CROSS_COUNTRY', "Women's Cross Country"), ('MENS_GOLF', "Men's Golf"), ('WOMENS_GOLF', "Women's Golf"), ('MENS_TENNIS', "Men's Tennis"), ('WOMENS_TENNIS', "Women's Tennis"), ('MENS_RUGBY', "Men's Rugby"), ('WOMENS_RUGBY', "Women's Rugby"), ('SAILING', 'Sailing'), ('MENS_WATER_POLO', "Men's Water Polo")])),
                ('is_exchange', models.CharField(max_length=3, verbose_name='Are you an Exchange Student?', choices=[('YES', 'yes'), ('NO', 'no')], blank=True)),
                ('is_fysep', models.CharField(max_length=3, verbose_name='Are you participating in the First Year Student Enrichment Program (FYSEP)?', choices=[('YES', 'yes'), ('NO', 'no')], blank=True)),
                ('is_international', models.CharField(max_length=3, verbose_name='Are you an International Student who plans on attending the International Student Orientation?', choices=[('YES', 'yes'), ('NO', 'no')], blank=True)),
                ('is_native', models.CharField(max_length=3, verbose_name='Are you a Native American Student who plans on attending the Native American student orientation?', choices=[('YES', 'yes'), ('NO', 'no')], blank=True)),
                ('is_transfer', models.CharField(max_length=3, verbose_name='Are you a Transfer Student?', choices=[('YES', 'yes'), ('NO', 'no')], blank=True)),
                ('available_sections', models.ManyToManyField(related_name='available_trippees', to='trips.Section', blank=True)),
                ('available_triptypes', models.ManyToManyField(related_name='available_trippees', to='trips.TripType', verbose_name='available types of trips', blank=True)),
                ('preferred_sections', models.ManyToManyField(related_name='prefering_trippees', to='trips.Section', blank=True)),
                ('preferred_triptypes', models.ManyToManyField(related_name='preferring_trippees', to='trips.TripType', verbose_name='preferred types of trips', blank=True)),
                ('unavailable_sections', models.ManyToManyField(related_name='unavailable_trippees', to='trips.Section', blank=True)),
                ('unavailable_triptypes', models.ManyToManyField(related_name='unavailable_trippees', to='trips.TripType', verbose_name='unavailable trip types', blank=True)),
                ('firstchoice_triptype', models.ForeignKey(related_name='firstchoice_triptype', to='trips.TripType', verbose_name='first choice trip types', null=True, blank=True)),
                ('epipen', models.CharField(max_length=3, verbose_name='Do you carry an EpiPen? If yes, please bring it with you on Trips.', blank=True, choices=[('YES', 'yes'), ('NO', 'no')], default='NO')),
                ('allergy_reaction', models.TextField(verbose_name='If you have a food allergy, please describe what happens when you come into contact with the allergen (e.g. I get hives, I go into anaphylactic shock).', blank=True, default='')),
                ('allergy_severity', models.PositiveIntegerField(null=True, verbose_name='If you have a food allergy, please rate the severity of the allergy on a scale from 1 to 5 (1 = itchy skin, puffy eyes and 5 = anaphylaxis).', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], blank=True)),
                ('sailing_experience', models.TextField(verbose_name='Please describe your sailing experience.', blank=True, default='')),
                ('phone', models.CharField(max_length=20, verbose_name='phone number')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='registration',
            field=models.OneToOneField(related_name='trippee', to='incoming.Registration', editable=False, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='trip_assignment',
            field=models.ForeignKey(related_name='trippees', to='trips.Trip', on_delete=django.db.models.deletion.PROTECT, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='trips_year',
            field=models.ForeignKey(to='db.TripsYear', editable=False, on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name='incomingstudent',
            old_name='dartmouth_email',
            new_name='blitz',
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='address',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='birthday',
            field=models.CharField(max_length=20),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='phone',
            field=models.CharField(max_length=30, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='ethnic_code',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='gender',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='incoming_status',
            field=models.CharField(max_length=20, choices=[('EXCHANGE', 'Exchange'), ('TRANSFER', 'Transfer'), ('FIRSTYEAR', 'First Year')], blank=True),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='name',
            field=models.CharField(max_length=512),
        ),
        migrations.AlterField(
            model_name='incomingstudent',
            name='netid',
            field=doc.users.models.NetIdField(max_length=20),
        ),
        migrations.RunPython(
            code=lowercase_netids,
            reverse_code=None,
            atomic=True,
        ),
        migrations.DeleteModel(
            name='Address',
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='bus_assignment',
            field=models.ForeignKey(to='transport.Stop', on_delete=django.db.models.deletion.PROTECT, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='financial_aid',
            field=models.PositiveSmallIntegerField(verbose_name='percentage financial assistance', default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
            preserve_default=True,
        ),
        migrations.RunPython(
            code=null_to_zero,
            reverse_code=None,
            atomic=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='green_fund_donation',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterUniqueTogether(
            name='incomingstudent',
            unique_together=set([('netid', 'trips_year')]),
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='hide_med_info',
            field=models.BooleanField(verbose_name='Hide registration med info?', help_text="Medical information in this trippee's registration will NOT be exported to leader and croo packets.", default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='incomingstudent',
            name='med_info',
            field=models.TextField(help_text='Additional medical info not provided in the registration, or simplified information if some details do not need to be provided to leaders and croos.', blank=True),
            preserve_default=True,
        ),
    ]

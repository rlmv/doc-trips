# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def add_croo_qualifications(apps, schema_editor):

    TripsYear = apps.get_model('db', 'TripsYear')
    QualificationTags = apps.get_model('applications', 'QualificationTag')

    trips_year = TripsYear.objects.get(is_current=True)
    
    QualificationTags.objects.get_or_create(name='Safety Lead', trips_year=trips_year)
    QualificationTags.objects.get_or_create(name='Kitchen Witch/Wizard', trips_year=trips_year)
    QualificationTags.objects.get_or_create(name='Climbing Croo', trips_year=trips_year)
    QualificationTags.objects.get_or_create(name='Oak Hill Croo', trips_year=trips_year)
    QualificationTags.objects.get_or_create(name='Grant Croo', trips_year=trips_year)


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0043_auto_20150310_1052'),
    ]

    operations = [
        migrations.RunPython(add_croo_qualifications)
    ]

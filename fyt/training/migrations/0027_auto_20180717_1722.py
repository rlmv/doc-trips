# Generated by Django 2.0.6 on 2018-07-17 21:22

from django.db import migrations
from django.utils import timezone

import logging

log = logging.getLogger(__name__)


TARGET_YEARS = [2015, 2016, 2017]


def move_first_aid_certifications(apps, schema_editor):
    Attendee = apps.get_model('training', 'Attendee')
    FirstAidCertification = apps.get_model('training', 'FirstAidCertification')

    for trips_year in TARGET_YEARS:
        for attendee in Attendee.objects.filter(trips_year=trips_year):

            def create_from_attendee(name='', other=''):
                if other:
                    name = 'other'

                created = FirstAidCertification.objects.create(
                    volunteer=attendee.volunteer,
                    trips_year_id=trips_year,
                    name=name,
                    other=other,
                    verified=True,
                    expiration_date=timezone.datetime(1900, 1, 1, 0, 0)
                )
                log.info('%s - %s' % (name, other))

            if attendee.fa_cert == 'FA/CPR':
                create_from_attendee('FA')
                create_from_attendee('CPR')
            elif attendee.fa_cert not in ['', 'other']:
                create_from_attendee(attendee.fa_cert)

            if 'FA' in attendee.fa_other:
                create_from_attendee('FA')

            if 'CPR' in attendee.fa_other:
                create_from_attendee('CPR')

            if 'Lifeguard' in attendee.fa_other:
                create_from_attendee(other='Lifeguard')

            if 'WEMT' in attendee.fa_other:
                create_from_attendee('W-EMT')

            if 'W-EMT' in attendee.fa_other:
                create_from_attendee('W-EMT')

            if 'BLS' in attendee.fa_other:
                create_from_attendee(other='BLS')

            if 'OEC' in attendee.fa_other:
                create_from_attendee('OEC')

            if 'WFA' in attendee.fa_other:
                create_from_attendee('WFA')

            if 'EMT' in attendee.fa_other:
                create_from_attendee('EMT')

            if 'WFR' in attendee.fa_other:
                create_from_attendee('WFR')


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0026_firstaidcertification_verified'),
        ('applications', '0116_auto_20180416_1613')
    ]

    operations = [
        migrations.RunPython(move_first_aid_certifications)
    ]

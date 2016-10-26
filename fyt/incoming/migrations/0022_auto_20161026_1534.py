# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

"""
Move Registration section and triptype preferences to an M2M field
with a through object.
"""


def use_section_through_fields(apps, schema_editor):
    Registration = apps.get_model('incoming', 'Registration')
    Section = apps.get_model('trips', 'Section')
    SectionChoice = apps.get_model('incoming', 'SectionChoice')

    for reg in Registration.objects.all():
        all_sections = Section.objects.filter(trips_year=reg.trips_year)

        all_sections = dict(zip(all_sections, all_sections))

        def create_through_objects(sections, preference):
            for sxn in sections:
                # Create an intermediate object if we haven't already for this
                # section
                sxn = all_sections.pop(sxn, None)
                if sxn is not None:
                    SectionChoice.objects.create(
                        registration=reg,
                        section=sxn,
                        preference=preference
                    )

        create_through_objects(reg.preferred_sections.all(), 'PREFER')
        create_through_objects(reg.available_sections.all(), 'AVAILABLE')
        create_through_objects(reg.unavailable_sections.all(), 'NOT AVAILABLE')
        # Remaining sections without a marked preference:
        create_through_objects(list(all_sections), 'NOT AVAILABLE')


def use_triptype_through_fields(apps, schema_editor):
    Registration = apps.get_model('incoming', 'Registration')
    TripType = apps.get_model('trips', 'TripType')
    TripTypeChoice = apps.get_model('incoming', 'TripTypeChoice')

    for reg in Registration.objects.all():
        all_tts = TripType.objects.filter(trips_year=reg.trips_year)

        all_tts = dict(zip(all_tts, all_tts))

        def create_through_objects(triptypes, preference):
            for tt in triptypes:
                # Create an intermediate object if we haven't already for this
                tt = all_tts.pop(tt, None)
                if tt is not None:
                    TripTypeChoice.objects.create(
                        registration=reg,
                        triptype=tt,
                        preference=preference
                    )

        if reg.firstchoice_triptype:
            create_through_objects([reg.firstchoice_triptype], 'FIRST CHOICE')

        create_through_objects(reg.preferred_triptypes.all(), 'PREFER')
        create_through_objects(reg.available_triptypes.all(), 'AVAILABLE')
        create_through_objects(reg.unavailable_triptypes.all(), 'NOT AVAILABLE')
        # Remaining sections without a marked preference:
        create_through_objects(list(all_tts), 'NOT AVAILABLE')


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0021_auto_20161026_1533'),
    ]

    operations = [
        migrations.RunPython(use_section_through_fields),
        migrations.RunPython(use_triptype_through_fields)
    ]

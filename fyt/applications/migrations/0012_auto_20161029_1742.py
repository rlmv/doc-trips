# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


"""
Move LeaderApplication section and triptype preferences to an M2M field
with a through object.
"""


def use_section_through_fields(apps, schema_editor):
    LeaderSupplement = apps.get_model('applications', 'LeaderSupplement')
    Section = apps.get_model('trips', 'Section')
    SectionChoice = apps.get_model('applications', 'LeaderSectionChoice')

    for app in LeaderSupplement.objects.all():
        all_sections = Section.objects.filter(trips_year=app.trips_year)

        all_sections = dict(zip(all_sections, all_sections))

        def create_through_objects(sections, preference):
            for sxn in sections:
                # Create an intermediate object if we haven't already for this
                # section
                sxn = all_sections.pop(sxn, None)
                if sxn is not None:
                    SectionChoice.objects.create(
                        application=app,
                        section=sxn,
                        preference=preference
                    )

        create_through_objects(app.preferred_sections.all(), 'PREFER')
        create_through_objects(app.available_sections.all(), 'AVAILABLE')
        # Remaining sections without a marked preference:
        create_through_objects(list(all_sections), 'NOT AVAILABLE')


def use_triptype_through_fields(apps, schema_editor):
    LeaderSupplement = apps.get_model('applications', 'LeaderSupplement')
    TripType = apps.get_model('trips', 'TripType')
    TripTypeChoice = apps.get_model('applications', 'LeaderTripTypeChoice')

    for app in LeaderSupplement.objects.all():
        all_tts = TripType.objects.filter(trips_year=app.trips_year)
        all_tts = dict(zip(all_tts, all_tts))

        def create_through_objects(triptypes, preference):
            for tt in triptypes:
                # Create an intermediate object if we haven't already for this
                tt = all_tts.pop(tt, None)
                if tt is not None:
                    TripTypeChoice.objects.create(
                        application=app,
                        triptype=tt,
                        preference=preference
                    )
        create_through_objects(app.preferred_triptypes.all(), 'PREFER')
        create_through_objects(app.available_triptypes.all(), 'AVAILABLE')
        # Remaining sections without a marked preference:
        create_through_objects(list(all_tts), 'NOT AVAILABLE')


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0011_auto_20161029_1402'),
    ]

    operations = [
        migrations.RunPython(use_section_through_fields),
        migrations.RunPython(use_triptype_through_fields)
    ]

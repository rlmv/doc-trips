import json
import os

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from fyt.applications.models import ApplicationInformation, PortalContent
from fyt.db.models import TripsYear
from fyt.incoming.models import Settings
from fyt.raids.models import RaidInfo
from fyt.timetable.models import Timetable

DATA_DIR = os.path.join(settings.BASE_DIR, 'db/initial_data')


def load_initial_data(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)


class Command(BaseCommand):

    help = ("Load all data needed for a fresh database")
    args = 'trips_year'

    def handle(self, *args, **options):

        if len(args) != 1:
            self.stderr.write("trips_year is a required argument")
            return

        year = args[0]

        try:
            TripsYear.objects.current()
            self.stderr.write(
                "At least one TripsYear already exists in the database. "
                "Flush the database and try again."
            )
        except TripsYear.DoesNotExist:
            with transaction.atomic():

                trips_year = TripsYear.objects.create(
                    year=year, is_current=True
                )

                Timetable.objects.create()

                Settings.objects.create(
                    trips_year=trips_year,
                    **load_initial_data('settings.json')
                )

                ApplicationInformation.objects.create(
                    trips_year=trips_year,
                    **load_initial_data('app_info.json')
                )

                PortalContent.objects.create(
                    trips_year=trips_year,
                    **load_initial_data('portal_content.json')
                )

                RaidInfo.objects.create(
                    trips_year=trips_year,
                    **load_initial_data('raid_info.json')
                )

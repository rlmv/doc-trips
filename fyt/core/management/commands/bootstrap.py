import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from fyt.core.models import TripsYear


class Command(BaseCommand):
    help = "Load all data needed for a fresh database"

    def loaddata(self, fixture):
        call_command('loaddata', fixture, stdout=self.stdout)

    def handle(self, *args, **options):
        if TripsYear.objects.count() > 0:
            self.stderr.write(
                "At least one TripsYear already exists in the database. "
                "Flush the database and try again.")
            sys.exit(1)

        with transaction.atomic():
            self.loaddata('trips_year.json')
            self.loaddata('timetable.json')
            self.loaddata('incoming.json')
            self.loaddata('applications.json')
            self.loaddata('raids.json')
            self.loaddata('transport.json')

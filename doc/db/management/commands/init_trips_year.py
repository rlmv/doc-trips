

from django.core.management.base import BaseCommand

from doc.db.models import TripsYear

class Command(BaseCommand):

    args = '<trips_year>'
    help = 'Initialize the database with a current trips_year'

    def handle(self, *args, **options):
        
        try:
            trips_year = TripsYear.objects.current()
            msg = ('a current TripsYear (%d) already exists in the database')
            self.stderr.write(msg % trips_year.year)

        except TripsYear.DoesNotExist:
            if len(args) == 1:
                TripsYear.objects.create(year=args[0], is_current=True)

            

            
            
            
        

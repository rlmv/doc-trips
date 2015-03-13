
import csv

from django.db import models

from doc.db.models import TripsYear


class CollegeInfoManager(models.Manager):

    def create_from_csv_file(self, file, trips_year):
        """

        trips_year is a string

        Returns a tuple (created_students, already_existing_students).
        """

        trips_year = TripsYear.objects.get(pk=trips_year)
 
        info = []
        reader = csv.DictReader(file)
        for row in reader:

            kwargs = {
                'netid': row['Id'],
                'name': row['Formatted Fml Name'],
                'class_year': row['Class Year'],
                'gender': row['Gender'],
                'ethnic_code': row['Fine Ethnic Code'],
                'email': row['EMail'],
                'dartmouth_email': row['Blitz'],
            }
            kwargs['trips_year'] = trips_year

            info.append(self.model(**kwargs))

        def get_netids(incoming_students):
            return set(map(lambda x: x.netid, incoming_students))

        netids = get_netids(info)
        existing = self.model.objects.filter(trips_year=trips_year)
        existing_netids = get_netids(existing)

        netids_to_create = netids - existing_netids
        to_create = filter(lambda x: x.netid in netids_to_create, info)
        self.model.objects.bulk_create(to_create)

        ignored_netids = existing_netids & netids
        return (list(netids_to_create), list(ignored_netids))
        
       

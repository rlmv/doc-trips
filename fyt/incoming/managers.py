
import csv

from django.db import models
from django.db.models import Q

from fyt.db.models import TripsYear
from fyt.utils.choices import YES


def get_netids(incoming_students):
    """ Return a set of incoming_students' netids """
    return set(map(lambda x: x.netid, incoming_students))


class IncomingStudentManager(models.Manager):

    def unregistered(self, trips_year):
        return self.filter(trips_year=trips_year, registration__isnull=True)

    def available_for_trip(self, trip):
        """
        Return all incoming students who indicate on their 
        registration that they are available for, prefer, or have
        chosen trip as their first choice.

        Unregistered students are not included.
        """
        sxn_pref = Q(registration__preferred_sections=trip.section)
        sxn_avail = Q(registration__available_sections=trip.section)
        type_top = Q(registration__firstchoice_triptype=trip.template.triptype)
        type_pref = Q(registration__preferred_triptypes=trip.template.triptype)
        type_avail = Q(registration__available_triptypes=trip.template.triptype)

        qs = self
        if not trip.template.non_swimmers_allowed:  # swimmers only
            from fyt.incoming.models import Registration
            qs = qs.exclude(registration__swimming_ability=Registration.NON_SWIMMER)
        
        return (
            qs.filter(trips_year=trip.trips_year)
            .filter(sxn_pref | sxn_avail)
            .filter(type_top | type_pref | type_avail)
            .distinct()
        )


    def create_from_csv_file(self, file, trips_year):
        """
        Import incoming students from a CSV file. 

        If a student already exists in the database for this year, 
        ignore. We compare entries via netid. 
        
        Param trips_year is a string
        Returns a tuple (created_students, existing_students).

        TODO: parse/input incoming_status. How should this work?
        """

        trips_year = TripsYear.objects.get(pk=trips_year)
 
        reader = csv.DictReader(file)
            
        def parse_to_object(row):
            """ Parse a CSV row and return an incoming student object """
            if not row['Id']:
                return None
            return self.model(
                trips_year=trips_year,
                netid=row['Id'],
                name=row['Formatted Fml Name'],
                class_year=row['Class Year'],
                gender=row['Gender'],
                birthday=row['Birthday'],
                ethnic_code=row['Fine Ethnic Code'],
                email=row['EMail'],
                blitz=row['Blitz'],
                phone=row['PR Phone'],
                address="{}\n{}\n{}, {} {}\n{}".format(
                    row['PR Street 1'],
                    row['PR Street 2'],
                    row['PR City'], row['PR State'], row['PR Zip'],
                    row['Pr Nation Name']
                )
            )

        incoming = list(filter(None, map(parse_to_object, reader)))
        incoming_netids = get_netids(incoming)

        existing = self.model.objects.filter(trips_year=trips_year)
        existing_netids = get_netids(existing)

        netids_to_create = incoming_netids - existing_netids
        to_create = filter(lambda x: x.netid in netids_to_create, incoming)
        for obj in to_create:
            obj.save()

        ignored_netids = existing_netids & incoming_netids
        return (list(netids_to_create), list(ignored_netids))

    def _passengers_base_qs(self, trips_year, route, section):
        """
        Base queryset for passengers_to/from_hanover.
        """
        from fyt.transport.models import Route
        assert route.category == Route.EXTERNAL

        return self.filter(
            trips_year=trips_year,
            trip_assignment__section=section
        ).select_related(
            'bus_assignment_round_trip',
            'bus_assignment_to_hanover',
            'bus_assignment_from_hanover',
        )

    def passengers_to_hanover(self, trips_year, route, section):
        """
        Return all trippees assigned to ride on external
        bus route on section TO Hanover
        """
        qs = self._passengers_base_qs(
            trips_year, route, section
        ).filter(
            (Q(bus_assignment_round_trip__route=route) |
             Q(bus_assignment_to_hanover__route=route)),
        )
        return sorted(qs, key=lambda x: x.get_bus_to_hanover().distance)

    def passengers_from_hanover(self, trips_year, route, section):
        """
        Return all trippees assigned to ride on external
        bus route on section FROM Hanover
        """
        qs = self._passengers_base_qs(
            trips_year, route, section
        ).filter(
            (Q(bus_assignment_round_trip__route=route) |
             Q(bus_assignment_from_hanover__route=route)),
        )
        return sorted(qs, key=lambda x: x.get_bus_from_hanover().distance)

    def with_trip(self, trips_year):
        """
        All trippees who have a trip assignment
        """
        return self.filter(
            trips_year=trips_year, trip_assignment__isnull=False
        )

    def cancelled(self, trips_year):
        """
        All trippees who cancelled their trip
        """
        return self.filter(
            trips_year=trips_year, cancelled=True
        )


class RegistrationManager(models.Manager):

    def want_financial_aid(self, trips_year):
        """
        All registrations for trips_year requesting financial aid.
        """
        return self.filter(
            trips_year=trips_year, financial_assistance=YES
        )
     
    def want_bus(self, trips_year):
        """
        All registrations for trips_year requesting an external bus
        """
        return self.filter(trips_year=trips_year).exclude(
            bus_stop_round_trip=None,
            bus_stop_to_hanover=None,
            bus_stop_from_hanover=None
        )

    def unmatched(self, trips_year):
        """
        All registrations for trips_year which are not associated
        with an IncomingStudent object.
        """
        return self.filter(trips_year=trips_year, trippee__isnull=True)

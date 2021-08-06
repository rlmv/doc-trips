import csv

from django.db import models
from django.db.models import Q

from fyt.core.models import TripsYear


def get_netids(incoming_students):
    """ Return a set of incoming_students' netids """
    return set(x.netid for x in incoming_students)


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
        from fyt.incoming.models import Registration, FIRST_CHOICE, PREFER, AVAILABLE

        qs = self
        if trip.template.swimtest_required:
            qs = qs.exclude(registration__swimming_ability=Registration.NON_SWIMMER)

        section = trip.section
        triptype = trip.template.triptype

        return (
            qs.filter(trips_year=trip.trips_year)
            .filter(
                registration__registrationsectionchoice__section=section,
                registration__registrationsectionchoice__preference__in=(
                    [PREFER, AVAILABLE]
                ),
            )
            .filter(
                registration__registrationtriptypechoice__triptype=triptype,
                registration__registrationtriptypechoice__preference__in=(
                    [FIRST_CHOICE, PREFER, AVAILABLE]
                ),
            )
        )

    def create_from_sheet(self, sheet, trips_year):
        """
        Import incoming students from a pyexcel sheet.

        If a student already exists in the database for this year,
        ignore. We compare entries via netid.

        Param trips_year is a string
        Returns a tuple (created_students, existing_students).

        TODO: parse/input incoming_status. How should this work?
        """
        sheet.name_columns_by_row(0)
        rows = sheet.to_records()

        added = []
        ignored = []

        for row in rows:
            if row['Id']:
                incoming, created = self.get_or_create(
                    trips_year=trips_year,
                    netid=row['Id'],
                    defaults={
                        'name': row['Formatted Fml Name'],
                        'class_year': row['Class Year'],
                        'gender': row['Gender'],
                        'birthday': row['Birthday'],
                        'ethnic_code': row['Fine Ethnic Code'],
                        'email': row['Email'],
                        'blitz': row['Blitz'],
                        'phone': row['PR Phone'],
                        'address': "{}\n{}\n{}, {} {}\n{}".format(
                            row['PR Street 1'],
                            row['PR Street 2'],
                            row['PR City'],
                            row['PR State'],
                            row['PR Zip'],
                            row['PR Nation Name'],
                        ),
                        'med_info': row['Medical Info'],
                        'notes': row['Notes'],
                    },
                )

                if created:
                    added.append(incoming.netid)
                else:
                    ignored.append(incoming.netid)

        return (added, ignored)

    def update_hinman_boxes(self, sheet, trips_year):
        """
        Import hinman boxes from a pyexcel sheet.

        Given a spreadsheet file with a ``netid`` and ``hinman box`` column,
        update each IncomingStudent specified by netid with the
        given hinman box number.
        """
        NETID = 'netid'
        HINMAN_BOX = 'hinman box'

        sheet.name_columns_by_row(0)

        updated = []
        not_found = []
        for row in sheet.to_records():
            try:
                inc = self.get(netid=row[NETID], trips_year=trips_year)
            except self.model.DoesNotExist:
                not_found.append(row[NETID])
            else:
                inc.hinman_box = row[HINMAN_BOX]
                inc.save()
                updated.append(inc)

        return updated, not_found

    def _passengers_base_qs(self, trips_year, route, section):
        """
        Base queryset for passengers_to/from_hanover.
        """
        from fyt.transport.models import Route

        assert route.category == Route.EXTERNAL

        return self.filter(
            trips_year=trips_year, trip_assignment__section=section
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
        qs = self._passengers_base_qs(trips_year, route, section).filter(
            (
                Q(bus_assignment_round_trip__route=route)
                | Q(bus_assignment_to_hanover__route=route)
            )
        )
        return sorted(qs, key=lambda x: x.get_bus_to_hanover().distance)

    def passengers_from_hanover(self, trips_year, route, section):
        """
        Return all trippees assigned to ride on external
        bus route on section FROM Hanover
        """
        qs = self._passengers_base_qs(trips_year, route, section).filter(
            (
                Q(bus_assignment_round_trip__route=route)
                | Q(bus_assignment_from_hanover__route=route)
            )
        )
        return sorted(qs, key=lambda x: x.get_bus_from_hanover().distance)

    def with_trip(self, trips_year):
        """
        All trippees who have a trip assignment
        """
        return self.filter(trips_year=trips_year, trip_assignment__isnull=False)

    def cancelled(self, trips_year):
        """
        All trippees who cancelled their trip
        """
        return self.filter(trips_year=trips_year, cancelled=True)


class RegistrationManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('user')

    def want_financial_aid(self, trips_year):
        """
        All registrations for trips_year requesting financial aid.
        """
        return self.filter(trips_year=trips_year, financial_assistance=True)

    def want_bus(self, trips_year):
        """
        All registrations for trips_year requesting an external bus
        """
        return self.filter(trips_year=trips_year).exclude(
            bus_stop_round_trip=None,
            bus_stop_to_hanover=None,
            bus_stop_from_hanover=None,
        )

    def unmatched(self, trips_year):
        """
        All registrations for trips_year which are not associated
        with an IncomingStudent object.
        """
        return self.filter(trips_year=trips_year, trippee__isnull=True)

import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Row, Submit
from django import forms
from django.db import models
from django.db.models import Q

from fyt.incoming.models import Registration
from fyt.transport.models import Stop


EXCHANGE = 'is_exchange'
TRANSFER = 'is_transfer'
INTERNATIONAL = 'is_international'
NATIVE = 'is_native'
FYSEP = 'is_fysep'
BUS = 'bus'
ATHLETE = 'is_athlete'
ANY = 'ANY'
NO = 'NO'
BLANK = '-------'


class ExternalBusRequestFilter(django_filters.ChoiceFilter):
    """Filter registrations based on the bus they requested."""

    def __init__(self, trips_year, **kwargs):
        qs = Stop.objects.external(trips_year)

        # Some hackery so that we can get add the ANY option. Does not work
        # with the ModelChoiceFilter so we have to set up choices manually.
        choices = [(s.pk, s.name) for s in qs]
        choices.insert(0, ('', BLANK))
        choices.insert(1, (ANY, 'All Buses'))

        super().__init__(choices=choices, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        # Return all registrations which request *some* bus
        if value == ANY:
            return qs.exclude(
                Q(bus_stop_round_trip=None) &
                Q(bus_stop_to_hanover=None) &
                Q(bus_stop_from_hanover=None))

        return qs.filter(
            Q(bus_stop_round_trip=value) |
            Q(bus_stop_to_hanover=value) |
            Q(bus_stop_from_hanover=value))


class AthleteFilter(django_filters.ChoiceFilter):
    """Filter based on varsity team."""

    def __init__(self, *args, **kwargs):
        choices = list(Registration.ATHLETE_CHOICES)
        choices.insert(0, ('', BLANK))
        choices.insert(2, (ANY, 'All Athletes'))
        super().__init__(*args, choices=choices, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        if value == NO:
            return qs.filter(Q(is_athlete=NO) | Q(is_athlete=None))

        if value == ANY:
            return qs.exclude(Q(is_athlete=NO) | Q(is_athlete=None))

        return qs.filter(is_athlete=value)


class SelectBooleanFilter(django_filters.BooleanFilter):
    """
    Only filter if the field is True; we don't care about the difference
    between None and False.
    """

    def __init__(self, *args, **kwargs):
        kwargs.update({'widget': forms.CheckboxInput()})
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        return qs.filter(**dict([(self.name, True)]))


class RegistrationFilterSet(django_filters.FilterSet):

    class Meta:
        model = Registration
        fields = []

    def __init__(self, *args, **kwargs):
        trips_year = kwargs.pop('trips_year')
        super().__init__(*args, **kwargs)

        self.filters[EXCHANGE] = SelectBooleanFilter(EXCHANGE, label='Exchange')
        self.filters[TRANSFER] = SelectBooleanFilter(TRANSFER, label='Transfer')
        self.filters[INTERNATIONAL] = SelectBooleanFilter(
            INTERNATIONAL, label='International')
        self.filters[NATIVE] = SelectBooleanFilter(NATIVE, label='Native')
        self.filters[FYSEP] = SelectBooleanFilter(FYSEP, label='FYSEP')

        self.filters[BUS] = ExternalBusRequestFilter(
            trips_year, label='External Bus Request')

        self.filters[ATHLETE] = AthleteFilter(ATHLETE, label='Athletes')

        self.form.helper = FilterSetFormHelper(self.form)


class FilterSetFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def filter_row(filter):
            return Row(Div(filter, css_class='col-lg-12'))

        self.form_method = 'GET'
        self.layout = Layout(
            filter_row(EXCHANGE),
            filter_row(TRANSFER),
            filter_row(INTERNATIONAL),
            filter_row(NATIVE),
            filter_row(FYSEP),
            filter_row(ATHLETE),
            filter_row(BUS),
            filter_row(Submit('submit', 'Filter', css_class='btn-block'))
        )

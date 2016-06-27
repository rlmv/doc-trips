
import django_filters
from django import forms
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Div

from fyt.incoming.models import Registration
from fyt.transport.models import Stop

EXCHANGE = 'is_exchange'
TRANSFER = 'is_transfer'
INTERNATIONAL = 'is_international'
NATIVE = 'is_native'
FYSEP = 'is_fysep'
BUS = 'bus'


class BooleanFilter(django_filters.MethodFilter):
    """Only show registrations where ``field`` is True."""

    def __init__(self, field, **kwargs):

        def _filter(qs, value):
            if not value:
                return qs

            kwargs = dict([(field, True)])
            return qs.filter(**kwargs)

        widget = forms.CheckboxInput()
        super().__init__(action=_filter, widget=widget, **kwargs)


class ExternalBusRequestFilter(django_filters.ModelChoiceFilter):
    """Filter registrations based on the bus they requested."""

    def __init__(self, trips_year, **kwargs):
        qs = Stop.objects.external(trips_year)
        super().__init__(queryset=qs, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        return qs.filter(
            Q(bus_stop_round_trip=value) |
            Q(bus_stop_to_hanover=value) |
            Q(bus_stop_from_hanover=value)
        )


class RegistrationFilterSet(django_filters.FilterSet):

    class Meta:
        model = Registration

    def __init__(self, *args, **kwargs):
        trips_year = kwargs.pop('trips_year')
        super().__init__(*args, **kwargs)

        self.filters[EXCHANGE] = BooleanFilter(EXCHANGE, label='Exchange')
        self.filters[TRANSFER] = BooleanFilter(TRANSFER, label='Transfer')
        self.filters[INTERNATIONAL] = BooleanFilter(INTERNATIONAL,
                                                    label='International')
        self.filters[NATIVE] = BooleanFilter(NATIVE, label='Native')
        self.filters[FYSEP] = BooleanFilter(FYSEP, label='FYSEP')

        self.filters[BUS] = ExternalBusRequestFilter(
            trips_year, label='External Bus Request')

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
            filter_row(BUS),
            filter_row(Submit('submit', 'Filter', css_class='btn-block'))
        )


import django_filters
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Div

from fyt.incoming.models import Registration

EXCHANGE = 'is_exchange'
TRANSFER = 'is_transfer'
INTERNATIONAL = 'is_international'
NATIVE = 'is_native'
FYSEP = 'is_fysep'


def BooleanFilter(field, name):

    def _filter(qs, value):
        if not value:
            return qs

        kwargs = dict([(field, True)])
        return qs.filter(**kwargs)

    filter = django_filters.MethodFilter(action=_filter)
    filter.field.widget = forms.CheckboxInput()
    filter.field.label = name

    return filter


class RegistrationFilterSet(django_filters.FilterSet):

    class Meta:
        model = Registration

    def __init__(self, *args, **kwargs):
        trips_year = kwargs.pop('trips_year')
        super().__init__(*args, **kwargs)

        self.filters[EXCHANGE] = BooleanFilter(EXCHANGE, 'Exchange')
        self.filters[TRANSFER] = BooleanFilter(TRANSFER, 'Transfer')
        self.filters[INTERNATIONAL] = BooleanFilter(INTERNATIONAL, 'International')
        self.filters[NATIVE] = BooleanFilter(NATIVE, 'Native')
        self.filters[FYSEP] = BooleanFilter(FYSEP, 'FYSEP')

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
            filter_row(Submit('submit', 'Filter', css_class='btn-block'))
        )

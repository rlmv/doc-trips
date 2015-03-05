
from collections import namedtuple

import django_filters
from django.db.models import Q
from django import forms

from doc.applications.models import GeneralApplication
from doc.croos.models import Croo

ArbitraryChoice = namedtuple('ArbitraryChoice', ['value', 'display', 'action'])

class ArbitraryChoiceFilter(django_filters.ChoiceFilter):
    """
    TODO: move to utils, in general form
    """

    def __init__(self, *args, **kwargs):
        choices = list(map(lambda c: ArbitraryChoice(*c), self.choices))
        filter_choices = map(lambda c: (c.value, c.display), choices)
        self.actions = dict(map(lambda c: (c.value, c.action), choices))
        super(ArbitraryChoiceFilter, self).__init__(self, *args, choices=filter_choices, **kwargs)

    # (query_value, display value, method)
    choices = [
        ('any', '--', None),
        ('croo', 'Croo Applications', 'croo_applications'),
        ('leader', 'Leader Applications', 'leader_applications'),
        ('either', 'Leader OR Croo Applications', 'either_applications'),
        ('both', 'Leader AND Croo Applications', 'both_applications'),
    ]

    def croo_applications(self, qs):
        return qs.exclude(croo_supplement__document='')

    def leader_applications(self, qs):
        return qs.exclude(leader_supplement__document='')

    def either_applications(self, qs):
        return qs.exclude(Q(leader_supplement__document='') &
                          Q(croo_supplement__document=''))

    def both_applications(self, qs):
        return qs.exclude(Q(leader_supplement__document='') |
                          Q(croo_supplement__document=''))

    def filter(self, qs, value):
        if not value or not self.actions[value]:
            return qs
        action = getattr(self, self.actions[value])
        if not action:
            return qs
        return action(qs)
        

SUGGESTED_CROOS = 'croo_supplement__grades__potential_croos'

class ApplicationFilterSet(django_filters.FilterSet):

    class Meta:
        model = GeneralApplication
        fields = ['status', 'applicant', SUGGESTED_CROOS]

        order_by = [('applicant__name', 'Name'),]
            
    applicant = django_filters.MethodFilter(action='lookup_user')
    complete = ArbitraryChoiceFilter() # not associated with a specific field

    def lookup_user(self, queryset, value):
        return queryset.filter(
            applicant__name__icontains=value
        )

    def __init__(self, *args, **kwargs):
        
        trips_year = kwargs.pop('trips_year')
        
        super(ApplicationFilterSet, self).__init__(*args, **kwargs)

        # add a blank choice
        self.filters['status'].field.choices.insert(0, ('', 'Any'))
        self.filters['status'].field.label = 'Status'

        # add the suggested croos filter. we have to restrict the queryset, 
        # and use the widget
        self.filters[SUGGESTED_CROOS] = django_filters.ModelMultipleChoiceFilter(
            name=SUGGESTED_CROOS, 
            label='Suggested Croos',
            queryset=Croo.objects.filter(trips_year=trips_year), 
            widget=forms.CheckboxSelectMultiple
        )
        
        self.ordering_field.label = 'Order by'
        self.form.helper = FilterSetFormHelper(self.form)


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Div
from crispy_forms.bootstrap import FormActions, FieldWithButtons, InlineCheckboxes
    
class FilterSetFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super(FilterSetFormHelper, self).__init__(*args, **kwargs)

        self.form_method = 'GET'
        self.layout = Layout(
            Row(
                Div(InlineCheckboxes(SUGGESTED_CROOS), css_class='col-sm-12'),
            ),
            Row(
                Div('complete', css_class='col-sm-4'),
                Div('status', css_class='col-sm-3'),
                Div('applicant', css_class='col-sm-2'),
                Div('o', css_class='col-sm-2'),
                Div(Submit('submit', 'Filter', css_class='filter-submit'), css_class='col-sm-1'),
            )
        )


 

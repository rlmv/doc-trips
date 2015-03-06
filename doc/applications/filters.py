
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
KITCHEN_LEAD = 'croo_supplement__kitchen_lead_willing'
SAFETY_LEAD = 'croo_supplement__safety_lead_willing'

class ApplicationFilterSet(django_filters.FilterSet):

    class Meta:
        model = GeneralApplication
        fields = ['status', 'applicant', SUGGESTED_CROOS,
                  KITCHEN_LEAD, SAFETY_LEAD]

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

        self.filters[KITCHEN_LEAD].field.label = 'Kitchen Witch/Wizard'
        self.filters[KITCHEN_LEAD].field.widget = forms.CheckboxInput()

        self.filters[SAFETY_LEAD].field.label = 'Safety Lead'
        self.filters[SAFETY_LEAD].field.widget = forms.CheckboxInput()

        # add the suggested croos filter. we have to restrict the queryset, 
        # and use the widget
        self.filters[SUGGESTED_CROOS] = django_filters.ModelMultipleChoiceFilter(
            name=SUGGESTED_CROOS, 
            label='',
            queryset=Croo.objects.filter(trips_year=trips_year), 
            widget=forms.CheckboxSelectMultiple
        )
        
        self.ordering_field.label = 'Order by'
        self.form.helper = FilterSetFormHelper(self.form)


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Div, HTML
from crispy_forms.bootstrap import FormActions, FieldWithButtons, InlineCheckboxes
    
class FilterSetFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super(FilterSetFormHelper, self).__init__(*args, **kwargs)

        self.form_method = 'GET'
        self.layout = Layout(
            Row(
                Div('complete', css_class='col-sm-4'),
                Div('status', css_class='col-sm-3'),
                Div('applicant', css_class='col-sm-2'),
                Div('o', css_class='col-sm-2'),
                Div(Submit('submit', 'Filter', css_class='filter-submit'), css_class='col-sm-1'),
            ),
            Row(
                Div(HTML('<strong>Suggested Croos (ANY):</strong>'), css_class='col-sm-3 text-right'),
                Div(InlineCheckboxes(SUGGESTED_CROOS), css_class='col-sm-9'),
                css_class='filter-croos',
            ),
            Row(
                Div(HTML('<strong>Roles:</strong>'), css_class='col-sm-3 text-right'),
                Div(KITCHEN_LEAD, css_class='col-sm-3 filter-checkbox'),
                Div(SAFETY_LEAD, css_class='col-sm-2 filter-checkbox'),
                css_class='filter-roles',
            ),
        )


 

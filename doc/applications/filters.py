
from collections import namedtuple

import django_filters
from django.db.models import Q
from django import forms

from doc.applications.models import GeneralApplication, QualificationTag

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
        ('any', 'All Applications', None),
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

        
CROO_QUALIFICATIONS = 'croo_supplement__grades__qualifications'

class ApplicationFilterSet(django_filters.FilterSet):

    class Meta:
        model = GeneralApplication
        fields = ['status', CROO_QUALIFICATIONS]
            
    name = django_filters.MethodFilter(action='lookup_user_by_name')
    netid = django_filters.MethodFilter(action='lookup_user_by_netid')
    complete = ArbitraryChoiceFilter() # not associated with a specific field

    def lookup_user_by_name(self, queryset, value):
        return queryset.filter(
            applicant__name__icontains=value
        )

    def lookup_user_by_netid(self, queryset, value):
        if value == '':
            return queryset
        return queryset.filter(
            applicant__netid__iexact=value
        )

    def __init__(self, *args, **kwargs):
        
        trips_year = kwargs.pop('trips_year')
        
        super(ApplicationFilterSet, self).__init__(*args, **kwargs)

        # add a blank choice
        self.filters['status'].field.choices.insert(0, ('', 'Any'))
        self.filters['status'].field.label = 'Status'

        # add the suggested croos filter. we have to restrict the queryset, 
        # and use the widget
        self.filters[CROO_QUALIFICATIONS] = django_filters.ModelMultipleChoiceFilter(
            name=CROO_QUALIFICATIONS, 
            label='Croo Qualifications',
            queryset=QualificationTag.objects.filter(trips_year=trips_year), 
            widget=forms.CheckboxSelectMultiple
        )
        
        self.form.helper = FilterSetFormHelper(self.form)


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Div, HTML
from crispy_forms.bootstrap import FormActions, FieldWithButtons, InlineCheckboxes
    
class FilterSetFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super(FilterSetFormHelper, self).__init__(*args, **kwargs)

        self.form_method = 'GET'
        self.layout = Layout(
            Row('complete'),
            Row('status'),   
            Row('name'),
            Row('netid'),
            Row(InlineCheckboxes(CROO_QUALIFICATIONS)),
            Row(Submit('submit', 'Filter', css_class='btn-block')),
        )


 

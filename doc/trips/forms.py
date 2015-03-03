

from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from bootstrap3_datetime.widgets import DateTimePicker

from doc.applications.models import LeaderSupplement
from doc.trips.models import Section


class SectionForm(forms.ModelForm):
    """ Form for Section Create and Update views. """
    
    class Meta:
        model = Section
        widgets = {
            'leaders_arrive': DateTimePicker(options={'format': 'MM/DD/YYYY', 
                                                      'pickTime': False})
        }

    def __init__(self, *args, **kwargs):
        super(SectionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))


class TripLeaderAssignmentForm(forms.ModelForm):
    
    class Meta:
        model = LeaderSupplement
        fields = ['assigned_trip']
        widgets = {
            'assigned_trip': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(TripLeaderAssignmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse('db:assign_leader_to_trip',
                                          kwargs={'trips_year': kwargs['instance'].trips_year.year,
                                                  'leader_pk': kwargs['instance'].pk})
        self.helper.add_input(Submit('submit', 'Add', css_class='btn-xs'))


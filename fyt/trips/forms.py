

from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import InlineField
from bootstrap3_datetime.widgets import DateTimePicker

from fyt.applications.models import LeaderSupplement, GeneralApplication
from fyt.incoming.models import IncomingStudent
from fyt.trips.models import Section, Trip


class SectionForm(forms.ModelForm):
    """
    Form for Section Create and Update views.
    """
    class Meta:
        model = Section
        fields = '__all__'
        widgets = {
            'leaders_arrive': DateTimePicker(options={
                'format': 'MM/DD/YYYY', 'pickTime': False
            })
        }

    def __init__(self, *args, **kwargs):
        super(SectionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))


class LeaderAssignmentForm(forms.ModelForm):

    class Meta:
        model = GeneralApplication
        fields = ['assigned_trip']
        widgets = {
            'assigned_trip': forms.HiddenInput()
        }

    def __init__(self, trips_year, *args, **kwargs):
        super(LeaderAssignmentForm, self).__init__(*args, **kwargs)
        self.fields['assigned_trip'].queryset = (
            Trip.objects.filter(trips_year=trips_year)
        )

    def clean(self):
        """
        Change status to leader if trip assignment is successful
        """
        if self.cleaned_data.get('assigned_trip'):
            self.instance.status = GeneralApplication.LEADER
        return super(LeaderAssignmentForm, self).clean()


class TrippeeAssignmentForm(forms.ModelForm):
    
    class Meta:
        model = IncomingStudent
        fields = ['trip_assignment']
        widgets = {
            'trip_assignment': forms.HiddenInput()
        }

    def __init__(self, trips_year, *args, **kwargs):
        super(TrippeeAssignmentForm, self).__init__(*args, **kwargs)
        self.fields['trip_assignment'].queryset = (
            Trip.objects.filter(trips_year=trips_year)
        )
        self.helper = FormHelper(self)
        label = 'Assign to %s' % (
            Trip.objects.get(pk=self.data['trip_assignment'])
        )
        self.helper.add_input(Submit('submit', label))


class FoodboxFormsetHelper(FormHelper):

    layout = Layout(
        InlineField('name', readonly=True),
        Field('half_kickin'),
        InlineField('gets_supplemental'),
    )

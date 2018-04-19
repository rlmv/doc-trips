from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.bootstrap import InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms

from fyt.applications.models import Volunteer
from fyt.core.forms import TripsYearModelForm
from fyt.incoming.models import IncomingStudent
from fyt.trips.models import Section, Trip


class SectionForm(TripsYearModelForm):
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

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.add_input(Submit('submit', 'Submit'))
        return helper


class LeaderAssignmentForm(TripsYearModelForm):

    class Meta:
        model = Volunteer
        fields = ['trip_assignment']
        widgets = {
            'trip_assignment': forms.HiddenInput()
        }

    def clean(self):
        """
        Change status to leader if trip assignment is successful
        """
        if self.cleaned_data.get('trip_assignment'):
            self.instance.status = Volunteer.LEADER
        return super().clean()


class TrippeeAssignmentForm(TripsYearModelForm):

    class Meta:
        model = IncomingStudent
        fields = ['trip_assignment']
        widgets = {
            'trip_assignment': forms.HiddenInput()
        }

    @property
    def helper(self):
        helper = FormHelper(self)
        label = 'Assign to %s' % (
            Trip.objects.get(pk=self.data['trip_assignment'])
        )
        helper.add_input(Submit('submit', label))
        return helper


class FoodboxFormsetHelper(FormHelper):

    layout = Layout(
        InlineField('name', readonly=True),
        Field('half_kickin'),
        InlineField('gets_supplemental'),
    )

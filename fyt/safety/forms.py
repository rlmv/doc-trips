from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Fieldset, Layout, Row, Submit

from fyt.core.forms import TripsYearModelForm
from fyt.safety.models import Incident, IncidentUpdate


class IncidentForm(TripsYearModelForm):

    class Meta:
        model = Incident
        fields = [
            'trip',
            'where',
            'when',
            'caller',
            'caller_role',
            'caller_number',
            'injuries',
            'subject',
            'subject_role',
            'desc',
            'resp',
            'outcome',
            'follow_up',
        ]
        widgets = {
            'when': DateTimePicker(options={'format': 'MM/DD/YYYY HH:mm'})
        }

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.layout = IncidentFormLayout()
        return helper


IncidentFormLayout = lambda: Layout(
    HTML('<p><strong> Your are logged in as {{ user }} </strong></p>'),
    Row(
        Div('trip', css_class='col-sm-6'),
        Div('when', css_class='col-sm-6'),
    ),
    Field('where', rows=2),
    Row(
        Div('caller', css_class='col-sm-3'),
        Div('caller_role', css_class='col-sm-3'),
        Div('caller_number', css_class='col-sm-3'),
    ),
    Row(
        Div('injuries', css_class='col-sm-6'),
    ),
    Row(
        Div('subject', css_class='col-sm-3'),
        Div('subject_role', css_class='col-sm-3'),
    ),
    Field('desc', rows=3),
    Field('resp', rows=3),
    Field('outcome', rows=3),
    Field('follow_up', rows=3),
    Submit('submit', 'Report'),
)


IncidentUpdateFormLayout = lambda: Layout(
    Fieldset(
        'Add an Update (logged in as {{ user }})',
        Row(
            Div('caller', css_class='col-sm-3'),
            Div('caller_role', css_class='col-sm-3'),
            Div('caller_number', css_class='col-sm-3'),
        ),
        Field('update', rows=4),
    ),
    Submit('submit', 'Update')
)


class IncidentUpdateForm(TripsYearModelForm):

    class Meta:
        model = IncidentUpdate
        fields = '__all__'

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.layout = IncidentUpdateFormLayout()
        return helper

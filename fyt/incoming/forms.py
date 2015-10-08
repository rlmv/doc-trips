
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Fieldset, Field, Submit, Row, Div, HTML
from django import forms

from .models import Registration, IncomingStudent
from .layouts import RegistrationFormLayout, join_with_and
from fyt.incoming.models import Settings
from fyt.db.models import TripsYear
from fyt.transport.models import Stop
from fyt.trips.fields import TrippeeSectionChoiceField, TripChoiceField
from fyt.trips.models import Section, TripType, Trip


class RoundTripStopChoiceField(forms.ModelChoiceField):
    """
    Field for displaying an external transport Stop, with round trip prices
    """
    def label_from_instance(self, obj):
        return "{} - ${}".format(obj.name, obj.cost_round_trip)


class OneWayStopChoiceField(forms.ModelChoiceField):
    """
    Field for displaying an external transport Stop, with one-way prices
    """
    def label_from_instance(self, obj):
        return "{} - ${}".format(obj.name, obj.cost_one_way)


class RegistrationForm(forms.ModelForm):
    """
    Form for Trippee registration
    """
    class Meta:
        model = Registration
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        if instance:
            trips_year = instance.trips_year
        else:
            trips_year = TripsYear.objects.current()

        external_stops = Stop.objects.external(trips_year)
        self.fields['bus_stop_round_trip'] = RoundTripStopChoiceField(
            label="Bus stop (round-trip)",
            queryset=external_stops, required=False
        )
        self.fields['bus_stop_to_hanover'] = OneWayStopChoiceField(
            label="Bus stop (one-way TO Hanover)",
            queryset=external_stops, required=False
        )
        self.fields['bus_stop_from_hanover'] = OneWayStopChoiceField(
            label="Bus stop (one-way FROM Hanover)",
            queryset=external_stops, required=False
        )

        # show which sections are available for these choices
        self.fields['is_exchange'].help_text = join_with_and(Section.objects.exchange(trips_year))
        self.fields['is_international'].help_text = join_with_and(Section.objects.international(trips_year))
        self.fields['is_transfer'].help_text = join_with_and(Section.objects.transfer(trips_year))
        self.fields['is_native'].help_text = join_with_and(Section.objects.native(trips_year))
        self.fields['is_fysep'].help_text = join_with_and(Section.objects.fysep(trips_year))

        sections = Section.objects.filter(trips_year=trips_year)
        self.fields['preferred_sections'] = TrippeeSectionChoiceField(queryset=sections, required=False)
        self.fields['available_sections'] = TrippeeSectionChoiceField(queryset=sections, required=False)
        self.fields['unavailable_sections'] = TrippeeSectionChoiceField(queryset=sections, required=False)

        triptypes = TripType.objects.filter(trips_year=trips_year)
        self.fields['firstchoice_triptype'].queryset = triptypes
        self.fields['preferred_triptypes'].queryset = triptypes
        self.fields['available_triptypes'].queryset = triptypes
        self.fields['unavailable_triptypes'].queryset = triptypes

        for f in ['preferred_sections', 'available_sections',
                  'unavailable_sections', 'preferred_triptypes',
                  'available_triptypes', 'unavailable_triptypes']:
            self.fields[f].widget = forms.CheckboxSelectMultiple()
            self.fields[f].help_text = None
        self.fields['firstchoice_triptype'].empty_label = None
        self.fields['firstchoice_triptype'].widget = forms.RadioSelect()

        self.helper = FormHelper(self)

        settings = Settings.objects.get(trips_year=trips_year)
        kwargs = {
            'local_sections': Section.objects.local(trips_year),
            'not_local_sections': Section.objects.not_local(trips_year),
            'international_sections': Section.objects.international(trips_year),
            'trips_cost': settings.trips_cost,
            'doc_membership_cost': settings.doc_membership_cost,
            'contact_url': settings.contact_url,
        }
        self.helper.layout = RegistrationFormLayout(**kwargs)


class AssignmentForm(forms.ModelForm):
    """
    Form to assign an IncomingStudent to a trip and bus
    """
    class Meta:
        model = IncomingStudent
        fields = [
            'trip_assignment',
            'cancelled',
            'bus_assignment_round_trip',
            'bus_assignment_to_hanover',
            'bus_assignment_from_hanover'
        ]

    def __init__(self, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)
        trips_year = kwargs['instance'].trips_year
        self.fields['trip_assignment'] = TripChoiceField(
            required=False,
            queryset=(
                Trip.objects
                .filter(trips_year=trips_year)
                .select_related('template', 'template__triptype', 'section')
            )
        )
        ext_stops = Stop.objects.external(trips_year)
        self.fields['bus_assignment_round_trip'].queryset = ext_stops
        self.fields['bus_assignment_to_hanover'].queryset = ext_stops
        self.fields['bus_assignment_from_hanover'].queryset = ext_stops

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            'trip_assignment',
            'cancelled',
            'bus_assignment_round_trip',
            'bus_assignment_to_hanover',
            'bus_assignment_from_hanover',
            Submit('submit', 'Update'),
        )


class TrippeeInfoForm(forms.ModelForm):
    """
    Form for editing administrative trippee info
    """
    class Meta:
        model = IncomingStudent
        fields = (
            'notes',
            'financial_aid',
            'cancelled', 'cancelled_fee',
            'med_info', 'show_med_info',
            'decline_reason',
            'name', 'netid', 'class_year',
            'ethnic_code', 'gender', 'birthday',
            'incoming_status',
            'email', 'blitz', 'phone', 'address'
        )
        
    helper = FormHelper()
    helper.layout = Layout(
        Field('notes', rows=3),
        'financial_aid',
        'decline_reason',
        Fieldset(
            'Cancellations',
            Row(
                Div('cancelled', css_class='col-sm-5'),
                Div('cancelled_fee', css_class='col-sm-7'),
            ),
        ),
        Fieldset(
            'Medical Info',
            HTML(
                "<p> To protect trippee privacy, medical information provided "
                "by trippees in their registration is, by default, NOT "
                "exported to leader packets. Checking the box below will "
                "export this information to leader packets.</p>"
            ),
            'show_med_info',
            Field('med_info', rows=3),
        ),
        Fieldset(
            'Contact and Demographic Info',
            'name',
            'netid',
            'class_year',
            'ethnic_code',
            'gender',
            'birthday',
            'incoming_status',
            'email',
            'blitz',
            'phone',
            Field('address', rows=4),
        ),
        Submit('submit', 'Update')
    )


class UploadIncomingStudentsForm(forms.Form):
    """
    Form to upload data about incoming students
    """
    csv_file = forms.FileField(label='CSV file')

    def __init__(self, *args, **kwargs):
        super(UploadIncomingStudentsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))

import codecs
import io
import os

import pyexcel
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Fieldset, Layout, Row, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from .layouts import RegistrationFormLayout
from .models import (
    REGISTRATION_SECTION_CHOICES,
    REGISTRATION_TRIPTYPE_CHOICES,
    IncomingStudent,
    Registration,
    RegistrationSectionChoice,
    RegistrationTripTypeChoice,
)

from fyt.applications.forms import PreferenceHandler
from fyt.core.forms import TripsYearModelForm
from fyt.core.models import TripsYear
from fyt.incoming.models import Settings
from fyt.transport.models import Stop
from fyt.trips.fields import TripChoiceField
from fyt.trips.models import Section, Trip, TripType
from fyt.utils.choices import NOT_AVAILABLE
from fyt.utils.fmt import join_with_and, join_with_or


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


class SectionPreferenceHandler(PreferenceHandler):
    through_qs_name = 'registrationsectionchoice_set'
    through_creator = 'set_section_preference'
    data_field = 'preference'
    target_field = 'section'
    choices = REGISTRATION_SECTION_CHOICES
    default = NOT_AVAILABLE

    def formfield_label(self, section):
        return '{} &mdash; {}'.format(section.name, section.trippee_date_str())


class TripTypePreferenceHandler(PreferenceHandler):
    through_qs_name = 'registrationtriptypechoice_set'
    through_creator = 'set_triptype_preference'
    data_field = 'preference'
    target_field = 'triptype'
    choices = REGISTRATION_TRIPTYPE_CHOICES
    default = NOT_AVAILABLE

    def formfield_label(self, triptype):
        return triptype.name


class RegistrationForm(TripsYearModelForm):
    """
    Form for Trippee registration
    """

    class Meta:
        model = Registration
        exclude = ['section_choice', 'triptype_choice']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        sections = Section.objects.filter(trips_year=self.trips_year)
        self.section_handler = SectionPreferenceHandler(self, sections)
        self.fields.update(self.section_handler.get_formfields())

        triptypes = TripType.objects.visible(self.trips_year)
        self.triptype_handler = TripTypePreferenceHandler(self, triptypes)
        self.fields.update(self.triptype_handler.get_formfields())

        external_stops = Stop.objects.external(self.trips_year)
        self.fields['bus_stop_round_trip'] = RoundTripStopChoiceField(
            label="Bus stop (round-trip)", queryset=external_stops, required=False
        )
        self.fields['bus_stop_to_hanover'] = OneWayStopChoiceField(
            label="Bus stop (one-way TO Hanover)",
            queryset=external_stops,
            required=False,
        )
        self.fields['bus_stop_from_hanover'] = OneWayStopChoiceField(
            label="Bus stop (one-way FROM Hanover)",
            queryset=external_stops,
            required=False,
        )

        # Show which sections are available for these choices
        self.fields['is_exchange'].help_text = join_with_and(
            Section.objects.exchange(self.trips_year)
        )
        self.fields['is_international'].help_text = join_with_and(
            Section.objects.international(self.trips_year)
        )
        self.fields['is_transfer'].help_text = join_with_and(
            Section.objects.transfer(self.trips_year)
        )
        self.fields['is_native'].help_text = join_with_and(
            Section.objects.native(self.trips_year)
        )
        self.fields['is_fysep'].help_text = join_with_and(
            Section.objects.fysep(self.trips_year)
        )

    @property
    def helper(self):
        helper = FormHelper(self)

        settings = Settings.objects.get(trips_year=self.trips_year)
        kwargs = {
            'local_sections': Section.objects.local(self.trips_year),
            'not_local_sections': Section.objects.not_local(self.trips_year),
            'international_sections': Section.objects.international(self.trips_year),
            'trips_cost': settings.trips_cost,
            'doc_membership_cost': settings.doc_membership_cost,
            'contact_url': settings.contact_url,
        }
        helper.layout = RegistrationFormLayout(
            self.section_handler.formfield_names(),
            self.triptype_handler.formfield_names(),
            **kwargs
        )

        return helper

    def save(self, user=None):
        if self.instance.pk is None:
            self.instance.user = user
            self.instance.trips_year = self.trips_year

        with transaction.atomic():
            registration = super().save()
            self.section_handler.save()
            self.triptype_handler.save()

        return registration


class AssignmentForm(TripsYearModelForm):
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
            'bus_assignment_from_hanover',
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['trip_assignment'] = TripChoiceField(
            required=False,
            queryset=(
                Trip.objects.filter(trips_year=self.trips_year).select_related(
                    'template', 'template__triptype', 'section'
                )
            ),
        )
        ext_stops = Stop.objects.external(self.trips_year)
        self.fields['bus_assignment_round_trip'].queryset = ext_stops
        self.fields['bus_assignment_to_hanover'].queryset = ext_stops
        self.fields['bus_assignment_from_hanover'].queryset = ext_stops

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.layout = Layout(
            'trip_assignment',
            'cancelled',
            'bus_assignment_round_trip',
            'bus_assignment_to_hanover',
            'bus_assignment_from_hanover',
            Submit('submit', 'Update'),
        )
        return helper


class TrippeeInfoForm(TripsYearModelForm):
    """
    Form for editing administrative trippee info
    """

    class Meta:
        model = IncomingStudent
        fields = [
            'notes',
            'financial_aid',
            'cancelled',
            'cancelled_fee',
            'med_info',
            'hide_med_info',
            'decline_reason',
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
            'address',
            'hinman_box',
        ]

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
        Fieldset('Medical Info', 'hide_med_info', Field('med_info', rows=3)),
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
            'hinman_box',
        ),
        Submit('submit', 'Update'),
    )


class PyExcelFileForm(forms.Form):
    """
    Form to upload a CSV file.
    """

    spreadsheet = forms.FileField(
        help_text="Uploaded file may be in Excel or CSV format"
    )

    def __init__(self, trips_year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean_spreadsheet(self):
        if self.extension not in self.valid_formats:
            raise ValidationError(
                '.{} is not a valid spreadsheet format. Try converting the '
                'file to one of the following formats: {}.'.format(
                    self.extension, join_with_or(self.valid_formats)
                )
            )

    @property
    def valid_formats(self):
        return pyexcel.plugins.parsers.READERS.get_all_formats()

    @property
    def extension(self):
        f = self.files['spreadsheet']
        return os.path.splitext(f.name)[1].strip('.')

    def load_sheet(self):
        """
        Return a pyexcel sheet read from the uploaded file.
        """
        f = self.files['spreadsheet']

        # Remove BOM
        if f.read(len(codecs.BOM_UTF8)).startswith(codecs.BOM_UTF8):
            f = io.TextIOWrapper(f, encoding='utf-8-sig')

        # Convert byte-stream to strings
        elif self.extension == 'csv':
            f = io.TextIOWrapper(f)

        return pyexcel.get_sheet(file_type=self.extension, file_stream=f)

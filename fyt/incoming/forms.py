import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Fieldset, Field, Submit, Row, Div, HTML
from django import forms

from .models import Registration, IncomingStudent, PREFERENCE_CHOICES, SectionChoice
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


class SectionChoiceField(forms.MultiValueField):

    def __init__(self, sections, **kwargs):
        self.sections = sections
        self.choices = ((None, '------'),) + PREFERENCE_CHOICES

        fields = [forms.ChoiceField(choices=self.choices)
                  for s in sections]
        widget = SectionChoiceWidget(sections, self.choices)
        super().__init__(fields, widget=widget, **kwargs)

    def compress(self, data_list):
        return {s: c for s, c in zip(self.sections, data_list)}


class SectionChoiceWidget(forms.MultiWidget):

    def __init__(self, sections, choices):
        self.sections = sections
        widgets = [forms.Select(choices=choices) for s in sections]
        super().__init__(widgets)

    # TODO
    def decompress(self, value):
        print('decompress', value)
        if not value:
            return value

        return [c.preference for c in value]


    def format_output(self, rendered_widgets):
        id_regex = re.compile(r'id="([a-z0-9_]+)"')

        s = ""
        for section, widget in zip(self.sections, rendered_widgets):
            id_ = id_regex.search(widget).group(1)
            label = '<label for="{0}" class="control-label">{1}</label>'.format(
                id_, section)

            s += ('<div class="form-group">' + label + widget + '</div>')

        return s


class RegistrationForm(forms.ModelForm):
    """
    Form for Trippee registration
    """

    class Meta:
        model = Registration
        exclude = ['section_choice']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        if instance:
            trips_year = instance.trips_year
        else:
            trips_year = TripsYear.objects.current()

        sections = Section.objects.filter(trips_year=trips_year)
        if instance:
            initial = instance.sectionchoice_set.all()
        else:
            initial = None
        self.fields['section_preference'] = SectionChoiceField(
            sections, initial=initial)

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

#        self.fields['section_choice'].queryset = sections

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

    def save(self):
        registration = super().save()

        old_choices = self.instance.sectionchoice_set.all()
        old_choices = {sc.section: sc for sc in old_choices}

        print(old_choices)

        for section, preference in self.cleaned_data['section_preference'].items():
            old_choice = old_choices.pop(section, None)

            if old_choice is None:
                choice = SectionChoice.objects.create(
                    registration=registration,
                    section=section,
                    preference=preference,
                )
                print('old', choice)
            elif old_choice.preference != preference:
                print('changed', old_choice, 'to', preference)
                old_choice.preference = preference
                old_choice.save()

        # If a section is deleted, the choice will also be deleted.
        assert len(old_choices) == 0

        return registration


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
        super().__init__(*args, **kwargs)
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
        fields = [
            'notes',
            'financial_aid',
            'cancelled',
            'cancelled_fee',
            'med_info',
            'show_med_info',
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
            'hinman_box',
        ),
        Submit('submit', 'Update')
    )


class CSVFileForm(forms.Form):
    """
    Form to upload a CSV file.
    """
    csv_file = forms.FileField(label='CSV file')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))

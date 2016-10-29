import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Fieldset, Field, Submit, Row, Div, HTML
from django import forms

from .models import (Registration, IncomingStudent, RegistrationSectionChoice,
                     RegistrationTripTypeChoice, REGISTRATION_SECTION_CHOICES,
                     REGISTRATION_TRIPTYPE_CHOICES)
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


class _BaseChoiceField(forms.MultiValueField):
    """
    Base form field used for Section and TripType preferences for both
    Registrations and LeaderApplications.

    Use the concrete `SectionChoiceField` and `TripTypeChoiceField`.

    Forms using this field must call `save_preferences` in the form's `save`
    method.
    """
    _type_name = None
    _model = None
    _widget = None
    _choices = None

    def _preferences(self, instance):
        """Common accesor for existing choices on a model, either
        `sectionchoice_set` or `triptypechoice_set`.
        """
        attr = self._model.__name__.lower() + '_set'
        return getattr(instance, attr).all().order_by(self._type_name)

    def __init__(self, qs, instance, **kwargs):
        self.qs = qs
        self.choices = ((None, '------'),) + self._choices

        if instance:
            initial = self._preferences(instance)
        else:
            initial = None

        fields = [forms.ChoiceField(choices=self.choices) for s in qs]
        widget = self._widget(qs, self.choices)

        error_messages = {
            'required': 'You must select a preference for every {}'.format(
                self._type_name)
        }

        kwargs.update({
            'initial': initial,
            'widget': widget,
            'error_messages': error_messages,
        })

        super().__init__(fields, **kwargs)

    def clean(self, value):
        # Handle the (nonexistant) case where the queryset is empty
        # (This is mostly just to simplify some testing.)
        if isinstance(value, (list, tuple)) and len(value) == 0:
            return self.compress(value)
        return super().clean(value)

    # TODO: is it possible to have a race condition here if the name of a
    # section is changed in-between when the form is rendered and the
    # response is received?
    def compress(self, data_list):
        """Convert data from the widget to usable format."""
        assert len(data_list) == len(self.qs)
        return dict(zip(self.qs, data_list))

    def save_preferences(self, registration, cleaned_data):
        """Save the preferences for this registration. This should be called
        in the form's ``save`` method.

        ``cleaned_data`` is in the format returned by ``compress``.
        """
        old_choices = self._preferences(registration)
        old_choices = {getattr(c, self._type_name): c for c in old_choices}

        for target, preference in cleaned_data.items():
            old_choice = old_choices.pop(target, None)

            if old_choice is None:
                kwargs = {
                    self._type_name: target,
                    self._target_name: registration,
                    'preference': preference
                }
                choice = self._model.objects.create(**kwargs)
                print('new', choice)
            elif old_choice.preference != preference:
                print('changed', old_choice, 'to', preference)
                old_choice.preference = preference
                old_choice.save()

        # If a section is deleted, the choice will also be deleted.
        # We only get here if there is a race condition.
        assert len(old_choices) == 0


class _BaseChoiceWidget(forms.MultiWidget):

    def __init__(self, qs, choices):
        self.qs = qs
        widgets = [forms.Select(choices=choices) for x in qs]
        super().__init__(widgets)

    # TODO
    def decompress(self, value):
        if not value:
            return [None] * len(self.qs)

        return [x.preference for x in value]

    def format_output(self, rendered_widgets):
        id_regex = re.compile(r'id="([a-z0-9_-]+)"')

        s = ""
        for obj, widget in zip(self.qs, rendered_widgets):
            id_ = id_regex.search(widget).group(1)
            label = '<label for="{0}" class="control-label">{1}</label>'.format(
                id_, self.label_value(obj))

            s += ('<div class="form-group">' + label + widget + '</div>')

        return s

    def label_value(self, obj):
        """Field label to display for the object."""
        return str(obj)


class RegistrationSectionChoiceWidget(_BaseChoiceWidget):
    # TODO: override for Leader Section preferences
    def label_value(self, section):
        return '%s &mdash; %s' % (section.name, section.trippee_date_str())


class SectionChoiceField(_BaseChoiceField):
    _type_name = 'section'
    _target = 'registration'
    _model = RegistrationSectionChoice
    _widget = RegistrationSectionChoiceWidget
    _choices = REGISTRATION_SECTION_CHOICES


class TripTypeChoiceField(_BaseChoiceField):
    _type_name = 'triptype'
    _targe_name = 'registration'
    _model = RegistrationTripTypeChoice
    _widget = _BaseChoiceWidget
    _choices = REGISTRATION_TRIPTYPE_CHOICES


class RegistrationForm(forms.ModelForm):
    """
    Form for Trippee registration
    """

    class Meta:
        model = Registration
        exclude = [
            'section_choice',
            'triptype_choice',
            '_old_preferred_sections',
            '_old_available_sections',
            '_old_unavailable_sections',
            '_old_firstchoice_triptype',
            '_old_preferred_triptypes',
            '_old_available_triptypes',
            '_old_unavailable_triptypes'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        if instance:
            trips_year = instance.trips_year
        else:
            trips_year = TripsYear.objects.current()

        self.trips_year = trips_year

        sections = Section.objects.filter(trips_year=trips_year)
        self.fields['section_preference'] = SectionChoiceField(
            sections, instance=instance)

        triptypes = TripType.objects.filter(trips_year=trips_year)
        self.fields['triptype_preference'] = TripTypeChoiceField(
            triptypes, instance=instance)

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

        self.fields['section_preference'].save_preferences(
            registration, self.cleaned_data['section_preference'])

        self.fields['triptype_preference'].save_preferences(
            registration, self.cleaned_data['triptype_preference'])

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

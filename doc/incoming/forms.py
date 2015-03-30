
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from doc.db.models import TripsYear
from doc.incoming.models import Registration
from doc.incoming.layouts import RegistrationFormLayout, join_with_and
from doc.trips.models import Section, TripType
from doc.transport.models import Stop


class RegistrationForm(forms.ModelForm):
    """
    Form for incoming student trippee registration.
    
    # TODO: restrict Section and TripType fields to trips_year
    # (and any other ForeignKeys
    TODO: pull trips_cost, etc from DB.
    """

    class Meta:
        model = Registration

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        trips_year = TripsYear.objects.current()
        if kwargs.get('instance', None):
            assert (kwargs.get('instance').trips_year == trips_year, 
                    'trips_year needs to be passed in, in this case')

        self.fields['bus_stop'].queryset = Stop.objects.external(trips_year)

        # show which sections are available for these choices
        self.fields['is_exchange'].help_text = join_with_and(Section.objects.exchange(trips_year))
        self.fields['is_international'].help_text = join_with_and(Section.objects.international(trips_year))
        self.fields['is_transfer'].help_text = join_with_and(Section.objects.transfer(trips_year))
        self.fields['is_native'].help_text = join_with_and(Section.objects.native(trips_year))
        self.fields['is_fysep'].help_text = join_with_and(Section.objects.fysep(trips_year))

        sections = Section.objects.filter(trips_year=trips_year)
        self.fields['preferred_sections'].queryset = sections
        self.fields['available_sections'].queryset = sections
        self.fields['unavailable_sections'].queryset = sections

        triptypes = TripType.objects.filter(trips_year=trips_year)
        self.fields['preferred_triptypes'].queryset = triptypes
        self.fields['available_triptypes'].queryset = triptypes
        self.fields['unavailable_triptypes'].queryset = triptypes

        for f in ['preferred_sections', 'available_sections', 
                  'unavailable_sections', 'preferred_triptypes',
                  'available_triptypes', 'unavailable_triptypes']:
            self.fields[f].widget = forms.CheckboxSelectMultiple()
            self.fields[f].help_text = None

        self.helper = FormHelper(self)

        from doc.core.models import Settings
        settings = Settings.objects.get()
        kwargs = {
            'local_sections': Section.objects.local(trips_year),
            'not_local_sections': Section.objects.not_local(trips_year),
            'international_sections': Section.objects.international(trips_year),
            'trips_cost': settings.trips_cost,
            'doc_membership_cost': settings.doc_membership_cost,
            'contact_url': settings.contact_url,
        }
        self.helper.layout = RegistrationFormLayout(**kwargs)


class IncomingStudentsForm(forms.Form):

    csv_file = forms.FileField(label='CSV file')

    def __init__(self, *args, **kwargs):

        super(IncomingStudentsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        



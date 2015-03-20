
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from doc.db.models import TripsYear
from doc.trippees.models import Registration
from doc.trippees.layouts import RegistrationFormLayout
from doc.trips.models import Section
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
        
        self.helper = FormHelper(self)
        kwargs = {
            'local_sections': Section.objects.local(trips_year),
            'not_local_sections': Section.objects.not_local(trips_year),
            'international_sections': Section.objects.international(trips_year),
            'trips_cost': 220,
            'doc_membership_cost': 50,
            'contact_url': 'http://outdoors.dartmouth.edu/firstyear/contact.html',
        }
        self.helper.layout = RegistrationFormLayout(**kwargs)


class IncomingStudentsForm(forms.Form):

    csv_file = forms.FileField(label='CSV file')

    def __init__(self, *args, **kwargs):

        super(IncomingStudentsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        



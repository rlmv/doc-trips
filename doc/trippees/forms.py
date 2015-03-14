
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout

from doc.trippees.models import Registration


class RegistrationForm(forms.ModelForm):
    
    # TODO: restrict Section and TripType fields to trips_year
    # (and any other ForeignKeys
    
    class Meta:
        model = Registration

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))


class IncomingStudentsForm(forms.Form):

    csv_file = forms.FileField(label='CSV file')

    def __init__(self, *args, **kwargs):

        super(IncomingStudentsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        




from bootstrap3_datetime.widgets import DateTimePicker
from django import forms

from fyt.training.models import Attendee, Session


class SessionForm(forms.ModelForm):

    class Meta:
        model = Session
        fields = '__all__'

        widgets = {
            # See http://eonasdan.github.io/bootstrap-datetimepicker/
            # for more options.
            'time': DateTimePicker(options={
                'format': 'MM/DD/YYYY HH:mm',
                'inline': True,
                'sideBySide': True,
                'stepping': 15,
            })
        }


class SignupForm(forms.ModelForm):

    class Meta:
        model = Attendee
        fields = ['sessions']
        widgets = {
            'sessions': forms.CheckboxSelectMultiple()
        }

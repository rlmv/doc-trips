
from bootstrap3_datetime.widgets import DateTimePicker
from django import forms

from fyt.training.models import Session


class SessionForm(forms.ModelForm):

    class Meta:
        model = Session
        fields = '__all__'

        widgets = {
            'time': DateTimePicker(options={'inline': True})
        }

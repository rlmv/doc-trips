
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


class AttendanceForm(forms.ModelForm):
    """
    Form for updating attendance for a training session.

    ModelForms cannot edit reverse ManyToMany relationships, hence the custom
    field and overriden save method.
    """
    class Meta:
        model = Session
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['completed'] = forms.ModelMultipleChoiceField(
            queryset=self.instance.registered.all(),
            initial=self.instance.completed.all(),
            widget=forms.CheckboxSelectMultiple())

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        instance.completed.add(*self.cleaned_data['completed'])
        return instance


class SignupForm(forms.ModelForm):

    class Meta:
        model = Attendee
        fields = ['registered_sessions']
        widgets = {
            'registered_sessions': forms.CheckboxSelectMultiple()
        }

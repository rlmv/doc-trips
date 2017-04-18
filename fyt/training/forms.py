
from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Row, Submit
from django import forms

from fyt.training.models import Attendee, Session


DATE_OPTIONS = {
    'format': 'MM/DD/YYYY',
}

TIME_OPTIONS = {
    'format': 'HH:mm',
    'stepping': 15,
}


class SessionForm(forms.ModelForm):

    class Meta:
        model = Session
        fields = '__all__'

        widgets = {
            # See http://eonasdan.github.io/bootstrap-datetimepicker/
            # for more options.
            'date': DateTimePicker(options=DATE_OPTIONS),
            'start_time': DateTimePicker(options=TIME_OPTIONS),
            'end_time': DateTimePicker(options=TIME_OPTIONS)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            'training',
            Row(
                Div('date', css_class='col-sm-4'),
                Div('start_time', css_class='col-sm-4'),
                Div('end_time', css_class='col-sm-4'),
            ),
            Submit('submit', 'Save')
        )


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
        labels = {
            'registered_sessions': ''
        }


class AttendeeUpdateForm(forms.ModelForm):

    class Meta:
        model = Attendee
        fields = [
            'first_aid',
            'complete_sessions',
        ]
        widgets = {
            'complete_sessions': forms.CheckboxSelectMultiple()
        }

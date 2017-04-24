from collections import OrderedDict

from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Row, Submit
from django import forms

from fyt.applications.models import Volunteer
from fyt.training.models import Attendee, Session
from fyt.db.templatetags.links import make_link


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
            'complete_sessions',
        ]
        widgets = {
            'complete_sessions': forms.CheckboxSelectMultiple()
        }


class FirstAidForm(forms.ModelForm):

    class Meta:
        model = Volunteer
        fields = ['fa_cert', 'fa_other']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_data = OrderedDict([
            ('Name', make_link(self.instance.detail_url(), self.instance)),
            ('Status', self.instance.get_status_display())
        ])


class FirstAidFormset(forms.modelformset_factory(
        Volunteer, form=FirstAidForm, extra=0)):
    """
    A formset for all leaders, croo members, and people on the leader waitlist.
    """

    def __init__(self, trips_year, *args, **kwargs):
        qs = (Volunteer.objects.leaders(trips_year) |
              Volunteer.objects.croo_members(trips_year) |
              Volunteer.objects.leader_waitlist(trips_year))

        super().__init__(*args, queryset=qs, **kwargs)

    @property
    def helper(self):
        helper = FormHelper()
        # This is an overridden template in fyt/templates
        helper.template = 'bootstrap3/table_inline_formset.html'
        helper.add_input(Submit('submit', 'Save'))

        return    

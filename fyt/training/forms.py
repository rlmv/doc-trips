from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Row, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from fyt.applications.models import Volunteer
from fyt.core.forms import TripsYearModelForm
from fyt.core.templatetags.links import make_link
from fyt.training.models import Attendee, FirstAidCertification, Session
from fyt.training.templatetags.training import capacity_label
from fyt.utils.fmt import join_with_and
from fyt.utils.forms import ReadonlyFormsetMixin


DATE_OPTIONS = {
    'format': 'MM/DD/YYYY',
}

TIME_OPTIONS = {
    'format': 'HH:mm',
    'stepping': 15,
}


class SessionForm(TripsYearModelForm):

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

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.layout = Layout(
            'training',
            Row(
                Div('date', css_class='col-sm-4'),
                Div('start_time', css_class='col-sm-4'),
                Div('end_time', css_class='col-sm-4'),
            ),
            'location',
            Submit('submit', 'Save')
        )
        return helper


class SessionRegistrationForm(TripsYearModelForm):
    """
    Form used to update registered attendees on the backend.
    """
    class Meta:
        model = Session
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['registered'] = forms.ModelMultipleChoiceField(
            queryset=Attendee.objects.trainable(self.instance.trips_year),
            initial=self.instance.registered.all(),
            widget=forms.CheckboxSelectMultiple(),
            required=False)

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        # TODO: use something other than set for better handling of race
        # conditions?
        instance.registered.set(self.cleaned_data['registered'])
        return instance


class AttendanceForm(TripsYearModelForm):
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
            widget=forms.CheckboxSelectMultiple(),
            required=False)

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        # TODO: use something other than set for better handling of race
        # conditions?
        instance.completed.set(self.cleaned_data['completed'])
        return instance


class RegisteredSessionsField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, instance):
        return mark_safe('{} {}'.format(capacity_label(instance), instance))


class SignupForm(TripsYearModelForm):

    class Meta:
        model = Attendee
        fields = ['registered_sessions']
        field_classes = {
            'registered_sessions': RegisteredSessionsField
        }
        widgets = {
            'registered_sessions': forms.CheckboxSelectMultiple()
        }
        labels = {
            'registered_sessions': ''
        }

    def clean_registered_sessions(self):
        new_registrations = (
            set(self.cleaned_data['registered_sessions']) -
            set(self.instance.registered_sessions.all()))

        full = [session for session in new_registrations if session.full()]

        if full:
            raise ValidationError(
                "The following sessions are full: {}. Please choose another "
                "session. If this is the only time you can attend, please "
                "contact the Trip Leader Trainers directly.".format(
                    join_with_and(full)))

        return self.cleaned_data['registered_sessions']


class AttendeeUpdateForm(TripsYearModelForm):

    class Meta:
        model = Attendee
        fields = [
            'complete_sessions',
        ]
        widgets = {
            'complete_sessions': forms.CheckboxSelectMultiple()
        }

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.layout = Layout(
            'complete_sessions',
            Submit('submit', 'Save')
        )
        return helper


class FirstAidFormset(ReadonlyFormsetMixin, forms.modelformset_factory(
        Attendee, fields=['fa_cert', 'fa_other'], extra=0)):
    """
    A formset for all leaders, croo members, and people on the leader waitlist.

    This is rendered by crispy forms as a table. `readonly_data` specifies
    readonly values to inject into the table for each form instance.
    """
    readonly_data = [
        ('Name', 'get_name'),
        ('Status', 'get_status'),
    ]

    def __init__(self, trips_year, *args, **kwargs):
        qs = Attendee.objects.trainable(
            trips_year
        ).only(
            'volunteer__applicant__name',
            'volunteer__status',
            'volunteer__trips_year_id',
            'volunteer__id',
            'fa_cert',
            'fa_other',
        )
        super().__init__(*args, queryset=qs, **kwargs)

    def get_name(self, instance):
        return make_link(instance.detail_url(), instance)

    def get_status(self, instance):
        return instance.volunteer.get_status_display()


class FirstAidCertificationForm(forms.ModelForm):
    class Meta:
        model = FirstAidCertification
        fields = [
            'name',
            'other',
            'expiration_date'
        ]
        widgets = {
            'expiration_date': DateTimePicker(options=DATE_OPTIONS)
        }


class BaseFirstAidCertificationFormset(forms.BaseInlineFormSet):

    def __init__(self, trips_year, *args, **kwargs):
        self.trips_year = trips_year
        super().__init__(*args, **kwargs)

    def save(self):
        """
        Attach trips_year to all instances.
        """
        instances = super().save(commit=False)
        for instance in instances:
            instance.trips_year = self.trips_year
            instance.save()

        return instances

    @property
    def helper(self):
        helper = FormHelper()  # Don't pass formset instance
        helper.form_tag = False
        helper.template = 'bootstrap3/table_inline_formset.html'
        helper.layout = Layout(
            'name',
            'other',
            'expiration_date')
        return helper


FirstAidCertificationFormset = forms.inlineformset_factory(
    Volunteer,
    FirstAidCertification,
    formset=BaseFirstAidCertificationFormset,
    form=FirstAidCertificationForm,
    can_delete=False)


class BaseFirstAidVerificationFormset(forms.BaseInlineFormSet):

    def __init__(self, trips_year, **kwargs):
        super().__init__(**kwargs)
        self.trips_year = trips_year

    def save(self):
        """
        Attach trips_year to new instances.
        """
        instances = super().save(commit=False)
        for instance in instances:
            if instance.pk is None:
                instance.trips_year = self.trips_year
                instance.save()

        return instances

    @property
    def helper(self):
        helper = FormHelper()  # Don't pass formset instance
        helper.template = 'bootstrap3/table_inline_formset.html'
        helper.layout = Layout(
            'name',
            'other',
            'expiration_date',
            'verified')
        helper.add_input(Submit('submit', 'Save'))
        return helper


FirstAidVerificationFormset = forms.inlineformset_factory(
    Volunteer,
    FirstAidCertification,
    formset=BaseFirstAidVerificationFormset,
    fields=['name', 'other', 'expiration_date', 'verified'],
    widgets={'expiration_date': DateTimePicker(options=DATE_OPTIONS)},
    can_delete=True)

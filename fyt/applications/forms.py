from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Div, Field, Row
from crispy_forms.bootstrap import Alert
from bootstrap3_datetime.widgets import DateTimePicker

from fyt.applications.models import (
    GeneralApplication, CrooSupplement, LeaderSupplement,
    CrooApplicationGrade, LeaderApplicationGrade, QualificationTag,
    LeaderSectionChoice, LeaderTripTypeChoice, LEADER_SECTION_CHOICES,
    LEADER_TRIPTYPE_CHOICES)
from fyt.db.models import TripsYear
from fyt.trips.models import Section, TripType, Trip
from fyt.trips.fields import LeaderSectionChoiceField, TripChoiceField
from fyt.utils.forms import crispify

from fyt.incoming.forms import _BaseChoiceWidget, _BaseChoiceField


class TripAssignmentForm(forms.ModelForm):
    """
    Update a leader's assigned trip
    """
    class Meta:
        model = GeneralApplication
        fields = ['assigned_trip']

    assigned_trip = TripChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_trip'].queryset = (
            Trip.objects
            .filter(trips_year=kwargs['instance'].trips_year)
            .select_related('section', 'template', 'template__triptype')
        )
        self.fields['assigned_trip'].label = 'Trip Assignment'
        crispify(self, submit_text='Update Assignment')


class ApplicationForm(forms.ModelForm):

    class Meta:
        model = GeneralApplication
        fields = (
            'class_year',
            'hinman_box',
            'phone',
            'gender',
            'race_ethnicity',
            'summer_address',
            'tshirt_size',
            'from_where',
            'what_do_you_like_to_study',
            'personal_activities',
            'feedback',
            'food_allergies',
            'dietary_restrictions',
            'medical_conditions',
            'epipen',
            'needs',
            'medical_certifications',
            'medical_experience',
            'peer_training',
            'trippee_confidentiality',
            'in_goodstanding_with_college',
            'trainings',
            'spring_training_ok',
            'summer_training_ok',
            'hanover_in_fall',
            'role_preference',
            'leadership_style'
        )

        widgets = {
            'personal_activities': forms.Textarea(attrs={'rows': 4}),
            'feedback': forms.Textarea(attrs={'rows': 4}),
            'medical_certifications': forms.Textarea(attrs={'rows': 4}),
            'medical_experience': forms.Textarea(attrs={'rows': 4}),
            'peer_training': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, trips_year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = ApplicationLayout()


class CrooSupplementForm(forms.ModelForm):

    class Meta:
        model = CrooSupplement
        fields = (
            'document',
            'licensed',
            'college_certified',
            'sprinter_certified',
            'microbus_certified',
            'can_get_certified',
            'safety_lead_willing',
            'kitchen_lead_willing',
            'kitchen_lead_qualifications',
        )
        widgets = {
            'kitchen_lead_qualifications': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, trips_year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = CrooSupplementLayout()


class LeaderSectionChoiceWidget(_BaseChoiceWidget):
    # TODO: override for Leader Section preferences
    def label_value(self, section):
        return '%s &mdash; %s' % (section.name, section.leader_date_str())


class SectionChoiceField(_BaseChoiceField):
    _type_name = 'section'
    _target_name = 'application'
    _model = LeaderSectionChoice
    _widget = LeaderSectionChoiceWidget
    _choices = LEADER_SECTION_CHOICES


class TripTypeChoiceField(_BaseChoiceField):
    _type_name = 'triptype'
    _target_name = 'application'
    _model = LeaderTripTypeChoice
    _widget = _BaseChoiceWidget
    _choices = LEADER_TRIPTYPE_CHOICES


class LeaderSupplementForm(forms.ModelForm):

    # override ModelForm field defaults
    _old_preferred_sections = LeaderSectionChoiceField(queryset=None, required=False)
    _old_available_sections = LeaderSectionChoiceField(queryset=None, required=False)

    class Meta:
        model = LeaderSupplement

        fields = (
            '_old_preferred_sections',
            '_old_available_sections',
            '_old_preferred_triptypes',
            '_old_available_triptypes',
            'trip_preference_comments',
            'cannot_participate_in',
            'relevant_experience',
            'document'
        )

    def __init__(self, trips_year, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')

        sections = Section.objects.filter(trips_year=trips_year)
        self.fields['section_preference'] = SectionChoiceField(
            sections, instance=instance)

        triptypes = TripType.objects.filter(trips_year=trips_year)
        self.fields['triptype_preference'] = TripTypeChoiceField(
            triptypes, instance=instance)

        # Widget specifications are in __init__ because of
        # https://github.com/maraujop/django-crispy-forms/issues/303
        # This weird SQL behavior is also triggered when field.queryset
        # is specified after field.widget = CheckboxSelectMultiple.
        self.fields['_old_preferred_sections'].queryset = (
            Section.objects.filter(trips_year=trips_year)
        )
        self.fields['_old_preferred_sections'].widget = (
            forms.CheckboxSelectMultiple()
        )
        self.fields['_old_available_sections'].queryset = (
            Section.objects.filter(trips_year=trips_year)
        )
        self.fields['_old_available_sections'].widget = (
            forms.CheckboxSelectMultiple()
        )
        self.fields['_old_preferred_triptypes'].queryset = (
            TripType.objects.filter(trips_year=trips_year)
        )
        self.fields['_old_preferred_triptypes'].widget = (
            forms.CheckboxSelectMultiple()
        )
        self.fields['_old_available_triptypes'].queryset = (
            TripType.objects.filter(trips_year=trips_year)
        )
        self.fields['_old_available_triptypes'].widget = (
            forms.CheckboxSelectMultiple()
        )
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = LeaderSupplementLayout()

    def save(self):
        application = super().save()

        self.fields['section_preference'].save_preferences(
            application, self.cleaned_data['section_preference'])

        self.fields['triptype_preference'].save_preferences(
            application, self.cleaned_data['triptype_preference'])

        return application


class ApplicationStatusForm(forms.ModelForm):

    class Meta:
        model = GeneralApplication
        fields = ('status',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        crispify(self, submit_text='Update')


class ApplicationAdminForm(forms.ModelForm):

    class Meta:
        model = GeneralApplication
        fields = ['status', 'assigned_trip', 'assigned_croo', 'safety_lead']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            'status',
            HTML("{% include 'applications/_trip_preferences.html' %}"),
            'assigned_trip',
            HTML("{% include 'applications/_croo_members.html' %}"),
            'assigned_croo',
            'safety_lead',
            Submit('submit', 'Update'),
        )


TIMEPICKER_OPTIONS = {'format': 'MM/DD/YYYY', 'pickTime': False}

class CertificationForm(forms.ModelForm):

    class Meta:
        model = GeneralApplication
        fields = (
            'community_building',
            'risk_management',
            'wilderness_skills',
            'croo_training',
            'fa_cert', 'fa_other'
        )
        widgets = {
            'community_building': DateTimePicker(options=TIMEPICKER_OPTIONS),
            'risk_management': DateTimePicker(options=TIMEPICKER_OPTIONS),
            'wilderness_skills': DateTimePicker(options=TIMEPICKER_OPTIONS),
            'croo_training': DateTimePicker(options=TIMEPICKER_OPTIONS,)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.all().wrap(Div, css_class='col-sm-3')
        self.helper.all().wrap(Row)
        self.helper.add_input(Submit('submit', 'Update'))


NOT_USED_IN_SCORING = (
    "Answers in this section will not be used in the scoring process"
)


class ApplicationLayout(Layout):

    def __init__(self):
        super().__init__(
            Alert(
                content=NOT_USED_IN_SCORING,
                dismiss=False, css_class='alert-info'
            ),
            Row(
                Div('class_year', css_class='col-sm-3'),
                Div('gender', css_class='col-sm-3'),
                Div('race_ethnicity', css_class='col-sm-3'),
            ),
            Row(
                Div('hinman_box', css_class='col-sm-3'),
                Div('phone', css_class='col-sm-3'),
                Div('summer_address', css_class='col-sm-5'),
            ),
            Row(
                Div('tshirt_size', css_class='col-sm-3'),
            ),
            Field('from_where'),
            Field('what_do_you_like_to_study'),
            'personal_activities',
            'feedback',
            Fieldset(
                'Trainings',
                'medical_certifications',
                'medical_experience',
                'peer_training',
                HTML(
                    "<p><strong>If selected to be a DOC trip leader, you must "
                    "complete various trainings before Trips begins. These "
                    "trainings are important in providing leaders with the "
                    "proper skills to lead a fun and safe trip. The training "
                    "program includes 10-12 hours (not necessarily all at once) "
                    "of training sessions covering First Aid/CPR, Community "
                    "Building, Wilderness Skills, Risk Management, and "
                    "Trip-specific outdoor experience. Leaders can get PE "
                    "credit for the trainings. Croo members are also required "
                    "to complete First Aid and CPR training, as well as attend "
                    "Croo specific trainings. Sessions are offered throughout "
                    "the spring and summer terms.</strong></p>"
                ),
                'spring_training_ok',
                'summer_training_ok',
            ),
            Fieldset(
                'Additional Information',
                'hanover_in_fall',
                'role_preference',
                'leadership_style',
            ),
            Fieldset(
                'Medical Information',
                HTML(
                    "<p>(This information will not affect your candidacy)</p>"
                 ),
                Field('food_allergies', rows=3),
                Field('dietary_restrictions', rows=3),
                Field('medical_conditions', rows=3),
                'epipen',
                Field('needs', rows=3),
            ),
            Fieldset(
                'Notices',
                HTML(
                    "<p>You must agree to the following statements in order "
                    "to lead a Trip or participate on a Croo. Checking each "
                    "box indicates your acceptance of the conditions for your "
                    "participation in DOC Trips.</p>"
                ),
                'trippee_confidentiality',
                'in_goodstanding_with_college',
                'trainings',
            ),
        )


class LeaderSupplementLayout(Layout):

    def __init__(self):
        super().__init__(
            'section_preference',
            'triptype_preference',
            Fieldset(
                'Application',
                HTML(
                    '<p> Download the <a href="{% if information.leader_supplement_questions %}{{ information.leader_supplement_questions.url }}{% endif %}"> '
                    'Trip Leader Application</a>. Thoughtfully answer the '
                    'questions and upload your responses in a Word (.docx) '
                    'document. <strong>Leave the original application questions '
                    'in the document with your responses.</strong> Your Trip '
                    'Leader application will not be considered complete until '
                    'you have uploaded answers to these questions. Be sure to '
                    'save your application after uploading.</p>'
                ),
                'document',
            ),
            Fieldset(
                'Trip Leader Availability',
                Alert(
                    content=NOT_USED_IN_SCORING,
                    dismiss=False, css_class='alert-info'
                ),
                HTML(
                    "<p>Please indicate your availibity for each section and "
                    "type of trip. <strong>Preferred</strong> means you will "
                    "be most satisfied with this option; you can prefer more "
                    "than one option. <strong>Available</strong> means you "
                    "could do it. If you leave a choice blank it means you "
                    "absolutely cannot participate on those dates or in that "
                    "activity.</p>"
                ),
                Row(
                    Div('_old_preferred_sections', css_class='col-sm-3'),
                    Div('_old_available_sections', css_class='col-sm-3'),
                ),
                HTML(
                    '<p> {% include "applications/triptype_modal.html" %}</p>'
                ),
                Row(
                    Div('_old_preferred_triptypes', css_class='col-sm-3'),
                    Div('_old_available_triptypes', css_class='col-sm-3'),
                ),
                Field('relevant_experience', rows=4),
                Field('trip_preference_comments', rows=2),
                Field('cannot_participate_in', rows=2),
            ),
        )


class CrooSupplementLayout(Layout):

    def __init__(self):
        super().__init__(
            Fieldset(
                'Application',
                HTML("""<p> Download the <a href="{% if information.croo_supplement_questions %}{{ information.croo_supplement_questions.url }}{% endif %}">Croo Application</a>. Thoughtfully answer the questions and upload your responses in a Word (.docx) document. <strong>Leave the original application questions in the document with your responses.</strong> Your Croo application will not be considered complete until you have uploaded answers to these questions. Scroll down and click 'Save' after uploading your answers.</p>"""),
                'document',
            ),
            Fieldset(
                'Driving',
                'licensed',
                'college_certified',
                'sprinter_certified',
                'microbus_certified',
                'can_get_certified',
            ),
            Fieldset(
                'Croo Positions',
                HTML(
                    "<p>Every croo has at least one or more <strong>Safety "
                    "Leads</strong> who are responsible for medical care & "
                    "evacuations at their respective location (Hanover, the "
                    "Grant, etc). Safety Leads are an integral part of each "
                    "croo and, in addition to their medical responsibilities, "
                    "are included in all other croo activities.  If you have a "
                    "WFR, EMT, W-EMT, OEC, or equivalent medical certification, "
                    "you are qualified to be a Safety Lead. We will prioritize "
                    "people who have higher safety certifications (EMT, W-EMT) "
                    "and extensive safety experience.</p>"
                ),
                'safety_lead_willing',
                HTML(
                    "<p>Lodj Croo has two <strong>Kitchen Witches/Wizards</strong> "
                    "who are responsible for ordering, preparing, and cooking "
                    "all the food at the Lodj during Trips. This role includes "
                    "a significant amount of responsibility and requires some "
                    "additional time before Trips begins to assist in ordering "
                    "all the necessary food items for the Lodj. You are eligible "
                    "to be a Kitchen Witch/Wizard if you have worked at the "
                    "Moosilauke Ravine Lodge during its normal operations "
                    "(non-Trips).</p>"
                ),
                'kitchen_lead_willing',
                'kitchen_lead_qualifications',
            )
        )


class CrooApplicationGradeForm(forms.ModelForm):
    """
    Form for scoring Croo applications
    """
    class Meta:
        model = CrooApplicationGrade
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # CheckboxSelectMultiple in __init__ because
        # https://github.com/maraujop/django-crispy-forms/issues/303
        self.fields['qualifications'].widget = forms.CheckboxSelectMultiple()
        self.fields['qualifications'].queryset = QualificationTag.objects.filter(
            trips_year=TripsYear.objects.current())


class LeaderApplicationGradeForm(forms.ModelForm):
    """
    Form for scoring Leader applications
    """
    class Meta:
        model = LeaderApplicationGrade
        fields = '__all__'

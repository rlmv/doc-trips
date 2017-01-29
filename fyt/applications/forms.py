from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.bootstrap import Alert
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Fieldset, Layout, Row, Submit
from django import forms

from fyt.applications.models import (
    LEADER_SECTION_CHOICES,
    LEADER_TRIPTYPE_CHOICES,
    Answer,
    CrooApplicationGrade,
    CrooSupplement,
    GeneralApplication,
    LeaderApplicationGrade,
    LeaderSectionChoice,
    LeaderSupplement,
    LeaderTripTypeChoice,
    QualificationTag,
    Question,
)
from fyt.db.models import TripsYear
from fyt.incoming.forms import _BaseChoiceField, _BaseChoiceWidget
from fyt.trips.fields import TripChoiceField
from fyt.trips.models import Section, Trip, TripType
from fyt.utils.forms import crispify


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
            'spring_training_ok',
            'summer_training_ok',
            'hanover_in_fall',
            'role_preference',
            'leadership_style',
            'leader_willing',
            'croo_willing'
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

        self.questions = Question.objects.filter(
            trips_year=trips_year
        )

        if self.instance:
            self.old_answers = self.instance.answer_set.all()
        else:
            self.old_answers = []

        initial = {
            q: "" for q in self.questions
        }

        if self.instance:
            initial.update({
                a.question: a.answer for a in self.old_answers
            })

        for question in self.questions:
            self.fields[self._question_name(question)] = (
                self._question_field(question, initial[question])
            )

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = ApplicationLayout(
            [self._question_name(q) for q in self.questions]
        )

    def _question_name(self, question):
        """Name of a dynamic application question field."""
        return "question_{}".format(question.pk)

    def _question_field(self, question, initial):
        """Dynamically create a field for the question."""
        return forms.CharField(
            initial=initial,
            label=question.question,
            required=False,
            widget=forms.Textarea(attrs={'rows': 5})
        )

    def save_answers(self, instance):
        """
        Save answers to dynamic questions.
        """
        def get_answer(question):
            return self.cleaned_data[self._question_name(question)]

        unanswered_questions = set(self.questions)

        # Update old answers
        for answer in self.old_answers:
            new_answer = get_answer(answer.question)
            if new_answer != answer.answer:
                print('changed', answer.answer, 'to', new_answer)
                answer.answer = new_answer
                answer.save()

            unanswered_questions.remove(answer.question)

        # Save remaining new answers
        for q in unanswered_questions:
            answer = Answer.objects.create(
                question=q,
                application=instance,
                answer=get_answer(q)
            )
            print('new', answer)

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        self.save_answers(instance)

        return instance

    # TODO: get rid of the need for this
    def update_agreements(self, agreement_form):
        """Update the agreements submitted in the agreement form."""
        for f in agreement_form.fields:
            value = getattr(agreement_form.instance, f)
            setattr(self.instance, f, value)


class AgreementForm(forms.ModelForm):
    """
    An extra form that allows us to separate the agreements section from the
    rest of the general application form.

    Crispy forms doesn't allow a single ModelForm to be split into separate
    layouts.
    """

    class Meta:
        model = GeneralApplication
        fields = [
            'trippee_confidentiality',
            'in_goodstanding_with_college',
            'trainings',
        ]

    def __init__(self, trips_year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = AgreementLayout()


class AgreementLayout(Layout):
    def __init__(self):
        super().__init__(
            Fieldset(
                'Agreements',
                HTML(
                    "<p>You must agree to the following statements in order "
                    "to lead a Trip or participate on a Croo. Checking each "
                    "box indicates your acceptance of the conditions for your "
                    "participation in DOC Trips.</p>"
                ),
                'trippee_confidentiality',
                'in_goodstanding_with_college',
                'trainings',
            )
        )


class CrooSupplementForm(forms.ModelForm):

    class Meta:
        model = CrooSupplement
        fields = (
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

    class Meta:
        model = LeaderSupplement

        fields = (
            'trip_preference_comments',
            'cannot_participate_in',
            'relevant_experience',
        )

    def __init__(self, trips_year, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')

        sections = Section.objects.filter(trips_year=trips_year)
        self.fields['section_preference'] = SectionChoiceField(
            sections, instance=instance, label='Section Preference')

        triptypes = TripType.objects.visible(trips_year)
        self.fields['triptype_preference'] = TripTypeChoiceField(
            triptypes, instance=instance, label='Trip Type Preference')

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

    def __init__(self, dynamic_questions):
        super().__init__(
            Fieldset(
                'Dynamic questions',
                *dynamic_questions
            ),
            Fieldset(
                'Volunteer Roles',
                HTML(
                    'Please select which volunteer position(s) you are '
                    'applying for. This page serves as the application for '
                    'both croo and trip leader positions. When you check the '
                    'box for either and/or both positions, please be aware '
                    'of the commitment you are making to the program.'
                ),
                'leader_willing',
                'croo_willing',
                'role_preference',
            ),
            Fieldset(
                'General Information',
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
                'from_where',
                'what_do_you_like_to_study',
                'hanover_in_fall',
                'personal_activities',
                'feedback',
            ),
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
                'Application',
                'leadership_style',
            ),
            Fieldset(
                'Medical Information',
                Alert(
                    content="This information will not affect your candidacy",
                    dismiss=False, css_class='alert-info'
                ),
                Field('food_allergies', rows=3),
                Field('dietary_restrictions', rows=3),
                Field('medical_conditions', rows=3),
                'epipen',
                Field('needs', rows=3),
            ),
        )


class LeaderSupplementLayout(Layout):

    def __init__(self):
        super().__init__(
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
                    "could do it. <strong>Not Available</strong> means you "
                    "absolutely cannot participate on those dates or in that "
                    "activity.</p>"
                ),
                'section_preference',
                HTML(
                    '<p> {% include "applications/triptype_modal.html" %}</p>'
                ),
                'triptype_preference',
                Field('relevant_experience', rows=4),
                Field('trip_preference_comments', rows=2),
                Field('cannot_participate_in', rows=2),
            ),
        )


class CrooSupplementLayout(Layout):

    def __init__(self):
        super().__init__(
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

from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.bootstrap import Alert, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Fieldset, Layout, Row, Submit
from django import forms
from django.core.exceptions import ImproperlyConfigured

from fyt.applications.models import (
    LEADER_SECTION_CHOICES,
    LEADER_TRIPTYPE_CHOICES,
    Answer,
    CrooSupplement,
    LeaderSupplement,
    Question,
    Score,
    ScoreQuestion,
    ScoreValue,
    Volunteer,
    validate_word_count,
)
from fyt.core.forms import TripsYearModelForm
from fyt.core.models import TripsYear
from fyt.croos.models import Croo
from fyt.trips.fields import TripChoiceField
from fyt.trips.models import Section, Trip, TripType
from fyt.utils.choices import NOT_AVAILABLE
from fyt.utils.fmt import join_with_and
from fyt.utils.forms import crispify


class ApplicationForm(TripsYearModelForm):
    class Meta:
        model = Volunteer
        fields = (
            'class_year',
            'hinman_box',
            'phone',
            'gender',
            'race_ethnicity',
            'summer_address',
            'tshirt_size',
            'hometown',
            'academic_interests',
            'personal_activities',
            'feedback',
            'food_allergies',
            'dietary_restrictions',
            'medical_conditions',
            'epipen',
            'needs',
            'peer_training',
            'spring_training_ok',
            'summer_training_ok',
            'hanover_in_fall',
            'transfer_exchange',
            'role_preference',
            'leader_willing',
            'croo_willing',
        )

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.form_tag = False
        helper.layout = ApplicationLayout()
        return helper

    # TODO: get rid of the need for this
    def update_agreements(self, agreement_form):
        """Update the agreements submitted in the agreement form."""
        for f in agreement_form.fields:
            value = getattr(agreement_form.instance, f)
            setattr(self.instance, f, value)


class QuestionForm(TripsYearModelForm):
    """
    A form for answering dynamic application questions.
    """

    class Meta:
        model = Volunteer
        fields = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        questions = Question.objects.filter(trips_year=self.trips_year)
        self.question_handler = QuestionHandler(self, questions)
        self.fields.update(self.question_handler.get_formfields())

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.form_tag = False
        helper.layout = QuestionLayout(self.question_handler.formfield_names())
        return helper

    def save(self, **kwargs):
        self.question_handler.save()


class AgreementForm(TripsYearModelForm):
    """
    Form used to agree to the required conditions and submit the application.
    """
    class Meta:
        model = Volunteer
        fields = [
            'trippee_confidentiality',
            'in_goodstanding_with_college',
            'trainings',
        ]

    def clean(self):
        cleaned_data = super().clean()
        if not all(cleaned_data.get(f) for f in self._meta.fields):
            raise forms.ValidationError('You must agree to these conditions')
        return cleaned_data

    def save(self, **kwargs):
        self.instance.submitted = True
        super().save()

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.form_tag = False
        helper.layout = AgreementLayout()
        return helper


class AgreementLayout(Layout):
    def __init__(self):
        super().__init__(
            Fieldset(
                'Agreements',
                HTML(
                    "<p>You must agree to the following statements in order "
                    "to volunteer for Trips. Checking each box indicates your "
                    "acceptance of the conditions required to participate in "
                    "DOC Trips.</p>"
                ),
                'trippee_confidentiality',
                'in_goodstanding_with_college',
                'trainings',
            )
        )


class CrooSupplementForm(TripsYearModelForm):
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

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.form_tag = False
        helper.layout = CrooSupplementLayout()
        return helper


class PreferenceHandler:
    """
    Base class that handles section and triptype preferences and dynamic
    application questions.
    """

    # The name of the attribute on the instance which links to the queryset
    # of through objects
    through_qs_name = None

    # Name of the method on the instance which creates a new through object
    # with the specified (target, data) arguments.
    through_creator = None

    # The name of the extra data field on the through model
    data_field = None

    # The name of the field containing the other end of the M2M relationship
    # (section, triptype, etc.) on the through model
    target_field = None

    # Choices allowed in the data field of the through object
    choices = None

    def __init__(self, form, targets):
        self.form = form
        self.targets = targets

    def get_target(self, through):
        return getattr(through, self.target_field)

    def get_data(self, through):
        return getattr(through, self.data_field)

    def set_data(self, through, data):
        setattr(through, self.data_field, data)

    def through_qs(self, instance):
        return (
            getattr(instance, self.through_qs_name)
            .select_related(self.target_field)
            .all()
        )

    def create_through(self, instance, target, data):
        return getattr(instance, self.through_creator)(target, data)

    def formfield_label(self, target):
        """The label for the formfield."""
        raise ImproperlyConfigured('Implement `formfield_label`')

    def formfield_name(self, target):
        """The name of the choice form field."""
        return "{}_{}".format(self.target_field, target.pk)

    def formfield_names(self):
        """The names of all formfields created by this handler."""
        return [self.formfield_name(t) for t in self.targets]

    def formfield(self, target, initial):
        """Dynamically create a field for a target preference."""
        return forms.ChoiceField(
            initial=initial,
            choices=self.choices,
            required=True,
            label=self.formfield_label(target),
        )

    def get_formfields(self):
        """
        Get all formfields for these targets, populated with initial data.
        """
        initial = self.get_initial()

        return {
            self.formfield_name(t): self.formfield(t, initial[t]) for t in self.targets
        }

    def get_initial(self):
        """
        Get a dictionary of initial data, keyed by target.
        """
        initial = {t: self.default for t in self.targets}

        if self.form.instance:
            initial.update(
                {
                    self.get_target(pref): self.get_data(pref)
                    for pref in self.through_qs(self.form.instance)
                }
            )

        return initial

    def save(self):
        """
        Save the through objects.

        This must be called after the form's `save` method has been called.
        """

        def get_cleaned_data(target):
            return self.form.cleaned_data[self.formfield_name(target)]

        targets = set(self.targets)

        # Update old answers
        for pref in self.through_qs(self.form.instance):
            target = self.get_target(pref)
            new_data = get_cleaned_data(target)

            if new_data != self.get_data(pref):
                self.set_data(pref, new_data)
                pref.save()

            targets.remove(target)

        # Save new answers
        for t in targets:
            self.create_through(self.form.instance, t, get_cleaned_data(t))


class QuestionHandler(PreferenceHandler):
    """
    Handler for dynamic questions and answers.
    """

    through_qs_name = 'answer_set'
    through_creator = 'answer_question'
    data_field = 'answer'
    target_field = 'question'
    default = ''

    def formfield_label(self, question):
        return question.display_text

    def formfield_help_text(self, question):
        base_text = 'Leave this blank if you are only applying for a {} position'

        if question.leader_only:
            return base_text.format('crooling')
        elif question.croo_only:
            return base_text.format('trip leader')
        elif question.optional:
            return (
                'This question is optional. Your application will be '
                'considered complete even if you leave this question '
                'blank, and whether or not you choose to answer it will '
                'not affect the grading of your application.'
            )

    def formfield(self, question, initial):
        return forms.CharField(
            initial=initial,
            label=self.formfield_label(question),
            help_text=self.formfield_help_text(question),
            required=False,
            widget=forms.Textarea(attrs={'rows': 8}),
            validators=[validate_word_count],
        )


class SectionPreferenceHandler(PreferenceHandler):
    through_qs_name = 'leadersectionchoice_set'
    through_creator = 'set_section_preference'
    data_field = 'preference'
    target_field = 'section'
    choices = LEADER_SECTION_CHOICES
    default = NOT_AVAILABLE

    def formfield_label(self, section):
        types = []
        if section.is_exchange:
            types.append('Exchange')
        if section.is_transfer:
            types.append('Transfer')
        if section.is_fysep:
            types.append('FYSEP')
        if section.is_international:
            types.append('International Student Orientation')
        if section.is_native:
            types.append('Native American Orientation')

        if types:
            type_str = ' ({})'.format('/'.join(types))
        else:
            type_str = ''

        return '{} &mdash; {}{}'.format(
            section.name, section.leader_date_str(), type_str
        )


class TripTypePreferenceHandler(PreferenceHandler):
    through_qs_name = 'leadertriptypechoice_set'
    through_creator = 'set_triptype_preference'
    data_field = 'preference'
    target_field = 'triptype'
    choices = LEADER_TRIPTYPE_CHOICES
    default = NOT_AVAILABLE

    def formfield_label(self, triptype):
        return triptype.name


class LeaderSupplementForm(TripsYearModelForm):
    class Meta:
        model = LeaderSupplement

        fields = (
            'availability',
            'relevant_experience',
            'class_2_3_paddler',
            'ledyard_level_1',
            'ledyard_level_2',
            'paddling_experience',
            'climbing_course',
            'dmc_leader',
            'climbing_experience',
            'dmbc_leader',
            'biking_experience',
            'bike_maintenance_experience',
            'cnt_leader',
            'hiking_experience',
            'co_leader',
            'section_availability',
        )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        sections = Section.objects.filter(trips_year=self.trips_year)
        self.section_handler = SectionPreferenceHandler(self, sections)
        self.fields.update(self.section_handler.get_formfields())

        triptypes = TripType.objects.visible(self.trips_year)
        self.triptype_handler = TripTypePreferenceHandler(self, triptypes)
        self.fields.update(self.triptype_handler.get_formfields())

        self.fields['section_availability'].help_text = (
            'Sophomores, if you are available for more than {} please use '
            'the above space to explain how.'.format(
                join_with_and(Section.objects.sophomore_leaders_ok(self.trips_year))
            )
        )

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = LeaderSupplementLayout(
            self.section_handler.formfield_names(),
            self.triptype_handler.formfield_names(),
        )

    def save(self):
        application = super().save()

        self.section_handler.save()
        self.triptype_handler.save()

        return application


class ApplicationStatusForm(TripsYearModelForm):
    class Meta:
        model = Volunteer
        fields = ('status',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        crispify(self, submit_text='Update')


class ApplicationAdminForm(TripsYearModelForm):
    class Meta:
        model = Volunteer
        fields = [
            'status',
            'trip_assignment',
            'croo_assignment',
            'safety_lead',
            'deadline_extension',
        ]
        widgets = {
            'deadline_extension': DateTimePicker(options={'format': 'MM/DD/YYYY HH:mm'})
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields['trip_assignment'].queryset = self.fields[
            'trip_assignment'
        ].queryset.select_related('section', 'template', 'template__triptype')

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.layout = Layout(
            'status',
            'deadline_extension',
            HTML("{% include 'applications/_trip_preferences.html' %}"),
            'trip_assignment',
            HTML("{% include 'applications/_croo_members.html' %}"),
            'croo_assignment',
            'safety_lead',
            Submit('submit', 'Update'),
        )
        return helper


class ApplicationLayout(Layout):
    def __init__(self):
        super().__init__(
            Fieldset(
                'Volunteer Roles',
                HTML(
                    'Please select which volunteer position(s) you are '
                    'applying for. We encourage you to apply to both.'
                ),
                'leader_willing',
                'croo_willing',
                'role_preference',
            ),
            SectionAlert(
                'NON-GRADED SECTION',
                'Answers in these sections will NOT be used in the scoring process.',
            ),
            Fieldset(
                'General Information',
                Row(
                    Div('class_year', css_class='col-sm-3'),
                    Div('gender', css_class='col-sm-3'),
                    Div('race_ethnicity', css_class='col-sm-3'),
                ),
                Row(
                    Div('hinman_box', css_class='col-sm-3'),
                    Div('phone', css_class='col-sm-3'),
                    Div('tshirt_size', css_class='col-sm-3'),
                ),
                'summer_address',
                'hometown',
                'hanover_in_fall',
                'transfer_exchange',
                'academic_interests',
                Field('personal_activities', rows=4),
                Field('feedback', rows=4),
            ),
            Fieldset(
                'Medical Information',
                Field('food_allergies', rows=3),
                Field('dietary_restrictions', rows=3),
                Field('medical_conditions', rows=3),
                'epipen',
                Field('needs', rows=3),
            ),
            Fieldset(
                'Trainings',
                Field('peer_training', rows=4),
                HTML(
                    "<p>If selected to be a trip leader, you must complete training before Trips begins to ensure the safety and engagement of the first-years who you will be responsible for for five days and four nights. The position requires you to complete 9 hours of trip leader training in the spring OR summer term, 3 hours for a First Aid certification, and 3 hours for a CPR certification.</p>"
                    "<p>If selected to be a crooling, you will ensure the safety and engagement of hundreds of first-years and volunteers. The position requires you to complete 6+ hours of croo training (different hour requirements for different croos), 3 hours for a First Aid certification, and 3 hours for a CPR certification.</p>"
                    "<p>NOTE: Trip leaders are eligible for PE credit once they have completed trainings AND served their role in Trips. We are currently working with the PE department to provide this perk for croolings as well.</p>"
                    "<p><strong>Please select which terms you would be available to complete trip leader and croo trainings. (Trip leader and croo trainings are DOC Trips-specific, while First Aid and CPR certifications can be acquired off-campus.) Please indicate both if you are available for both.</strong></p>"
                ),
                'spring_training_ok',
                'summer_training_ok',
                Fieldset(
                    'First Aid Certifications',
                    HTML(
                        "<p>Please list all of your <strong>current</strong> first aid certifications and their expiration date. If your certification is not listed in the dropdown box, please list it in the 'other' field.</p>"
                    ),
                ),
            ),
        )


def SectionAlert(header, content):
    return Alert(
        dismiss=False,
        css_class='alert-info',
        content=('<h3>{}</h3> <p>{}</p>'.format(header, content)),
    )


class QuestionLayout(Layout):
    def __init__(self, dynamic_questions):
        super().__init__(
            SectionAlert(
                'GRADED SECTION',
                'This is the ONLY section that will be available to readers during the blind reading and scoring process. Each answer may be no longer than 300 words.',
            ),
            *dynamic_questions
        )


class LeaderSupplementLayout(Layout):
    def __init__(self, section_fields, triptype_fields):
        super().__init__(
            Fieldset(
                'Wilderness Experience',
                HTML(
                    "<p>As we mentioned before, outdoor ability is NOT "
                    "required to volunteer for Trips, but certain croos and "
                    "trips do require wilderness skills. These questions will "
                    "help us place you appropriately.</p>"
                ),
                'class_2_3_paddler',
                'ledyard_level_1',
                'ledyard_level_2',
                Field('paddling_experience', rows=2),
                'climbing_course',
                'dmc_leader',
                Field('climbing_experience', rows=2),
                'dmbc_leader',
                Field('biking_experience', rows=2),
                Field('bike_maintenance_experience', rows=2),
                'cnt_leader',
                Field('hiking_experience', rows=2),
            ),
            Fieldset(
                'Trip Leader Availability',
                HTML(
                    "<p>Please indicate your availabity for each section and "
                    "type of trip. <strong>Preferred</strong> means you will "
                    "be most satisfied with this option; you can prefer more "
                    "than one option. <strong>Available</strong> means you "
                    "could do it. <strong>Not Available</strong> means you "
                    "absolutely cannot participate on those dates or in that "
                    "activity.</p> "
                    "<p>Please keep in mind that your availability will "
                    "affect our ability to place you on a trip&mdash;the more "
                    "available you are, the more likely we will be able to "
                    "place you.</p>"
                ),
            ),
            Fieldset('Sections', *section_fields),
            Field('section_availability', rows=2),
            Fieldset(
                'Trip Types',
                HTML(
                    "<p>For trip leader applicants only. Please keep in "
                    "mind that your availability will affect our ability "
                    "to place you on a trip&mdash;the more available you "
                    "are, the more likely we will be able to place you.</p>"
                    '<p>{% include "applications/triptype_modal.html" %}</p>'
                ),
                *triptype_fields
            ),
            Field('relevant_experience', rows=3),
            Field('availability', rows=3),
            Field('co_leader', rows=3),
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
                    "Leads</strong> who are responsible for medical care and "
                    "evacuations at their respective location (Hanover, Grant, "
                    "Oak Hill, etc). Safety Leads are an integral part of each "
                    "croo and, in addition to their medical responsibilities, "
                    "are included in all other croo activities. If you have a "
                    "WFR, EMT, W-EMT, OEC, or equivalent medical certification, "
                    "you are qualified to be a Safety Lead. We will prioritize "
                    "people who have higher safety certifications (EMT, W-EMT) "
                    "and extensive safety experience.</p>"
                ),
                'safety_lead_willing',
                HTML(
                    "<p>Lodj Croo has one <strong>Kitchen Magician</strong> "
                    "who is responsible for ordering, preparing, and cooking "
                    "all the food at the Lodj during Trips. This role includes "
                    "a significant amount of responsibility and requires some "
                    "additional time before Trips begins to assist in ordering "
                    "all the necessary food items for the Lodj. You are eligible "
                    "to be a Kitchen Magician if you have worked at the "
                    "Moosilauke Ravine Lodge during its normal operations "
                    "(non-Trips) or have other experience cooking in "
                    "industrial kitchens.</p>"
                ),
                'kitchen_lead_willing',
                Field('kitchen_lead_qualifications', rows=2),
            ),
        )


class CommentHandler(PreferenceHandler):
    """
    Handler for comments on dynamic answers
    """

    through_qs_name = 'scorecomment_set'
    through_creator = 'add_comment'
    data_field = 'comment'
    target_field = 'score_question'
    default = ''

    def formfield_label(self, score_question):
        return str(score_question)

    def formfield(self, answer, initial):
        return forms.CharField(
            initial=initial,
            label=self.formfield_label(answer),
            help_text='',  # self.formfield_help_text(answer),
            required=False,
            widget=forms.Textarea(attrs={'rows': 2}),
        )


class ScoreValueChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.verbose_str()


SKIP = 'skip'


def ScoreForm(application, grader, **kwargs):
    """
    Return a form to score this application.

    We only display leader_score/croo_score fields if the application is a
    leader/croo application.
    """
    # Select appropriate score fields
    score_fields = []
    if application.leader_application_complete:
        score_fields.append('leader_score')
    if application.croo_application_complete:
        score_fields.append('croo_score')

    class _ScoreForm(TripsYearModelForm):
        """
        The dynamically generated form class.
        """

        class Meta:
            model = Score
            fields = ['general'] + score_fields
            field_classes = {f: ScoreValueChoiceField for f in score_fields}

        def __init__(self, application, grader, **kwargs):
            super().__init__(trips_year=application.trips_year, **kwargs)
            self.grader = grader
            self.application = self.instance.application = application
            self.score_questions = ScoreQuestion.objects.filter(
                trips_year=self.trips_year
            )
            self.comment_handler = CommentHandler(self, self.score_questions)
            self.fields.update(self.comment_handler.get_formfields())

        @property
        def helper(self):
            helper = FormHelper(self)

            helper.layout = Layout(
                *self.comment_handler.formfield_names(),
                *score_fields,
                Field('general', rows=3),
                FormActions(
                    Submit('submit', 'Submit Score'),
                    Submit(
                        SKIP,
                        'Skip this Application',
                        css_class='btn-warning',
                        formnovalidate=True,  # Disable browser validation
                    ),
                )
            )
            return helper

        def save(self, **kwargs):
            self.instance.grader = self.grader
            self.instance.application = self.application
            self.instance.trips_year = self.trips_year
            score = super().save()
            self.comment_handler.save()
            return score

    return _ScoreForm(application, grader, **kwargs)


class ScoreQuestionFormset(
    forms.models.modelformset_factory(
        ScoreQuestion,
        extra=2,
        fields=['question', 'order'],
        can_delete=True,
        widgets={'question': forms.Textarea(attrs={'rows': 2})},
    )
):
    """
    Formset used to setup scoring for the year.
    """

    def __init__(self, trips_year, *args, **kwargs):
        self.trips_year = trips_year
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('submit', 'Save'))
        return helper

    def save(self):
        for form in self.extra_forms:
            if form.has_changed():
                form.instance.trips_year = self.trips_year
        return super().save()

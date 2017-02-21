from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.bootstrap import Alert
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Fieldset, Layout, Row, Submit
from django import forms
from django.core.exceptions import ImproperlyConfigured

from fyt.applications.models import (
    LEADER_SECTION_CHOICES,
    LEADER_TRIPTYPE_CHOICES,
    Answer,
    CrooApplicationGrade,
    CrooSupplement,
    GeneralApplication,
    LeaderApplicationGrade,
    LeaderSupplement,
    QualificationTag,
    Question,
)
from fyt.db.models import TripsYear
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
            'height',
            'weight',
            'gear',
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
            'transfer_exchange',
            'role_preference',
            'leader_willing',
            'croo_willing'
        )

    def __init__(self, trips_year, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = ApplicationLayout()

    # TODO: get rid of the need for this
    def update_agreements(self, agreement_form):
        """Update the agreements submitted in the agreement form."""
        for f in agreement_form.fields:
            value = getattr(agreement_form.instance, f)
            setattr(self.instance, f, value)


class QuestionForm(forms.Form):
    """
    A form for answering dynamic application questions.
    """

    def __init__(self, trips_year, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.instance = instance

        questions = Question.objects.filter(trips_year=trips_year)
        self.question_handler = QuestionHandler(self, questions)
        self.fields.update(self.question_handler.get_formfields())

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = QuestionLayout(
            self.question_handler.formfield_names()
        )

    def save(self, **kwargs):
        self.question_handler.save()


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
                    "to volunteer for Trips. Checking each box indicates your "
                    "acceptance of the conditions required to participate in "
                    "DOC Trips.</p>"
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

    def __init__(self, trips_year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = CrooSupplementLayout()


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
        return getattr(instance, self.through_qs_name).all()

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
            label=self.formfield_label(target)
        )

    def get_formfields(self):
        """
        Get all formfields for these targets, populated with initial data.
        """
        initial = self.get_initial()

        return {
            self.formfield_name(t): self.formfield(t, initial[t])
            for t in self.targets
        }

    def get_initial(self):
        """
        Get a dictionary of initial data, keyed by target.
        """
        initial = {t: "" for t in self.targets}

        if self.form.instance:
            initial.update({
                self.get_target(pref): self.get_data(pref)
                for pref in self.through_qs(self.form.instance)
            })

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

    def formfield_label(self, question):
        return question.question

    def formfield(self, question, initial):
        return forms.CharField(
            initial=initial,
            label=self.formfield_label(question),
            required=False,
            widget=forms.Textarea(attrs={'rows': 8})
        )


class SectionPreferenceHandler(PreferenceHandler):
    through_qs_name = 'leadersectionchoice_set'
    through_creator = 'set_section_preference'
    data_field = 'preference'
    target_field = 'section'
    choices = LEADER_SECTION_CHOICES

    def formfield_label(self, section):
        return '%s &mdash; %s' % (section.name, section.leader_date_str())


class TripTypePreferenceHandler(PreferenceHandler):
    through_qs_name = 'leadertriptypechoice_set'
    through_creator = 'set_triptype_preference'
    data_field = 'preference'
    target_field = 'triptype'
    choices = LEADER_TRIPTYPE_CHOICES

    def formfield_label(self, triptype):
        return triptype.name


class LeaderSupplementForm(forms.ModelForm):

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
        )


    def __init__(self, trips_year, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sections = Section.objects.filter(trips_year=trips_year)
        self.section_handler = SectionPreferenceHandler(self, sections)
        self.fields.update(self.section_handler.get_formfields())

        triptypes = TripType.objects.visible(trips_year)
        self.triptype_handler = TripTypePreferenceHandler(self, triptypes)
        self.fields.update(self.triptype_handler.get_formfields())

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = LeaderSupplementLayout(
            self.section_handler.formfield_names(),
            self.triptype_handler.formfield_names())

    def save(self):
        application = super().save()

        self.section_handler.save()
        self.triptype_handler.save()

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
                'Answers in these sections will NOT be used in the scoring process.'
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
                'from_where',
                'what_do_you_like_to_study',
                'hanover_in_fall',
                'transfer_exchange',
                Field('personal_activities', rows=4),
                Field('feedback', rows=4),
            ),
            Fieldset(
                'Gear',
                HTML(
                    "<p>We will use this information to fit gear for you on "
                    "trips that require it (e.g. paddles and life jackets for "
                    "canoeing and kayaking trips, harnesses for climbing "
                    "trips, etc.)</p>"
                ),
                Row(
                    Div('height', css_class='col-sm-3'),
                    Div('weight', css_class='col-sm-3'),
                ),
                Field('gear', rows=3),
            ),
            Fieldset(
                'Trainings',
                Field('medical_certifications', rows=4),
                Field('medical_experience', rows=4),
                Field('peer_training', rows=4),
                HTML(
                    "<p>If selected to be a trip leader, you must complete training before Trips begins to ensure the safety and engagement of the first-years who you will be responsible for for five days and four nights. The position requires you to complete 9 hours of trip leader training in the spring OR summer term, 3 hours for a First Aid certification, and 3 hours for a CPR certification.</p>"
                    "<p>If selected to be a crooling, you will ensure the safety and engagement of hundreds of first-years and volunteers. The position requires you to complete 6+ hours of croo training (different hour requirements for different croos), 3 hours for a First Aid certification, and 3 hours for a CPR certification.</p>"
                    "<p>NOTE: Trip leaders are eligible for PE credit once they have completed trainings AND served their role in Trips. We are currently working with the PE department to provide this perk for croolings as well.</p>"
                    "<p><strong>Please select which terms you would be available to complete trip leader and croo trainings. (Trip leader and croo trainings are DOC Trips-specific, while First Aid and CPR certifications can be acquired off-campus.) Please indicate both if you are available for both.</strong></p>"
                ),
                'spring_training_ok',
                'summer_training_ok',
            ),
            Fieldset(
                'Medical Information',
                Field('food_allergies', rows=3),
                Field('dietary_restrictions', rows=3),
                Field('medical_conditions', rows=3),
                'epipen',
                Field('needs', rows=3),
            ),
        )


def SectionAlert(header, content):
    return Alert(
        dismiss=False, css_class='alert-info', content=(
            '<h3>{}</h3> <p>{}</p>'.format(header, content)
        )
    )


class QuestionLayout(Layout):

    def __init__(self, dynamic_questions):
        super().__init__(
            SectionAlert(
                'GRADED SECTION',
                'This is the ONLY section that will be available to readers during the blind reading and scoring process.'
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
                    "trips do require wilderness skills, so these questions "
                    "will help us place you appropriately.</p>"
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
            Fieldset(
                'Sections',
                *section_fields
            ),
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
                    "are included in all other croo activities.  If you have a "
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

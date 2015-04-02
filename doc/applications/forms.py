

from django import forms
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Div, Field, MultiField, Row, Column
from crispy_forms.bootstrap import Alert
from bootstrap3_datetime.widgets import DateTimePicker

from doc.applications.models import (GeneralApplication, CrooSupplement, LeaderSupplement,
                                     CrooApplicationGrade, LeaderApplicationGrade)
from doc.db.models import TripsYear
from doc.trips.models import Section, TripType, ScheduledTrip
from doc.utils.forms import crispify


class ScheduledTripChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}{}: {}: {}".format(
            obj.section, obj.template.name,
            obj.template.triptype.name,
            obj.template.description_summary
        )


class TripAssignmentForm(forms.ModelForm):
    """ Update a leader's assigned trip """

    class Meta:
        model = GeneralApplication
        fields = ['assigned_trip']
    assigned_trip = ScheduledTripChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        super(TripAssignmentForm, self).__init__(*args, **kwargs)
        self.fields['assigned_trip'].queryset = (
            ScheduledTrip.objects
            .filter(trips_year=kwargs['instance'].trips_year)
            .select_related('section', 'template', 'template__triptype')
        )
        crispify(self, submit_text='Update Assignment')
       

class ApplicationForm(forms.ModelForm):
    
    class Meta:
        model = GeneralApplication
        fields = (
            'class_year', 'hinman_box', 'phone', 'gender', 'race_ethnicity', 
            'summer_address', 'tshirt_size',
            'from_where', 'what_do_you_like_to_study', 
            'personal_activities', 'feedback',
            'dietary_restrictions', 'allergen_information', 
            'medical_certifications', 'medical_experience', 'peer_training',
            'trippee_confidentiality', 'in_goodstanding_with_college',
            'trainings', 'spring_training_ok', 'summer_training_ok',
            'hanover_in_fall', 'role_preference',
        )
        
        widgets = {
            'dietary_restrictions': forms.Textarea(attrs={'rows': 2}),
            'allergen_information': forms.Textarea(attrs={'rows': 2}),
            'personal_activities': forms.Textarea(attrs={'rows': 4}),
            'feedback': forms.Textarea(attrs={'rows': 4}),
            'medical_certifications': forms.Textarea(attrs={'rows': 4}),
            'medical_experience': forms.Textarea(attrs={'rows': 4}),
            'peer_training': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = ApplicationLayout()
        

class CrooSupplementForm(forms.ModelForm):

    class Meta:
        model = CrooSupplement
        fields = (
            'document', 
            'safety_lead_willing', 
            'kitchen_lead_willing', 'kitchen_lead_qualifications',
        )
        widgets = {
            'kitchen_lead_qualifications': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(CrooSupplementForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = CrooSupplementLayout()


class SectionChoiceField(forms.ModelMultipleChoiceField):
    """
    Custom field to display section information
    """
    def label_from_instance(self, obj):
        return mark_safe(str(obj) + ' &mdash; '  + obj.date_range_str())


class LeaderSupplementForm(forms.ModelForm):

    # override ModelForm field defaults
    preferred_sections = SectionChoiceField(queryset=None, required=False)
    available_sections = SectionChoiceField(queryset=None, required=False)
    
    class Meta:
        model = LeaderSupplement

        fields = (
            'preferred_sections', 'available_sections', 
            'preferred_triptypes', 'available_triptypes',
            'trip_preference_comments', 'cannot_participate_in',
            'relevant_experience', 'document'
        )

    def __init__(self, *args, **kwargs):
        super(LeaderSupplementForm, self).__init__(*args, **kwargs)

        # Restrict querysets to current trips year
        # TODO: since this form is used by the database update view, 
        # pass the trips year in explicitly to support previous years,
        # OR don't allow editing of old trips_years.
        trips_year = TripsYear.objects.current()
        if kwargs.get('instance', None):
            assert kwargs['instance'].trips_year == trips_year

        # Widget specifications are in __init__ because of 
        # https://github.com/maraujop/django-crispy-forms/issues/303
        # This weird SQL behavior is also triggered when field.queryset 
        # is specified after field.widget = CheckboxSelectMultiple.
        self.fields['preferred_sections'].queryset = (
            Section.objects.filter(trips_year=trips_year)
        )
        self.fields['preferred_sections'].widget = (
            forms.CheckboxSelectMultiple()
        )
        self.fields['available_sections'].queryset = (
            Section.objects.filter(trips_year=trips_year)
        )
        self.fields['available_sections'].widget = (
            forms.CheckboxSelectMultiple()
        )
        self.fields['preferred_triptypes'].queryset = (
            TripType.objects.filter(trips_year=trips_year)
        )
        self.fields['preferred_triptypes'].widget = (
            forms.CheckboxSelectMultiple()
        )
        self.fields['available_triptypes'].queryset = (
            TripType.objects.filter(trips_year=trips_year)
        )
        self.fields['available_triptypes'].widget = (
            forms.CheckboxSelectMultiple()
        )
        
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = LeaderSupplementLayout()


class ApplicationAdminForm(forms.ModelForm):

    class Meta:
        model = GeneralApplication
        fields = ('status',)

    def __init__(self, *args, **kwargs):
        super(ApplicationAdminForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Update'))
        

TIMEPICKER_OPTIONS = {'format': 'MM/DD/YYYY', 'pickTime': False}

class LeaderSupplementAdminForm(forms.ModelForm):

    class Meta:
        model = LeaderSupplement
        fields = ('community_building', 'risk_management', 
                  'wilderness_skills', 'first_aid')

        widgets = {
            'community_building': DateTimePicker(options=TIMEPICKER_OPTIONS),
            'risk_management': DateTimePicker(options=TIMEPICKER_OPTIONS),
            'wilderness_skills': DateTimePicker(options=TIMEPICKER_OPTIONS),
            'first_aid': DateTimePicker(options=TIMEPICKER_OPTIONS),
        }

    def __init__(self, *args, **kwargs):
        super(LeaderSupplementAdminForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.all().wrap(Div, css_class='col-sm-3')
        self.helper.all().wrap(Row)
        self.helper.add_input(Submit('submit', 'Update'))


class ApplicationLayout(Layout):

    def __init__(self):
        
        super(ApplicationLayout, self).__init__(

                Alert(content='Answers in this section will NOT be used in the scoring process',
                      dismiss=False, css_class='alert-info'),

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
                Field('from_where'), #disabled=True),
                Field('what_do_you_like_to_study'), # disabled=True),
                'personal_activities',
                'feedback',
            Fieldset(
                'Trainings',
                'medical_certifications', 
                'medical_experience', 
                'peer_training',
                HTML("<p><strong>If selected to be a DOC trip leader, you must complete various trainings before Trips begins. These trainings are important in providing leaders with the proper skills to lead a fun and safe trip. The training program includes 10-12 hours (not necessarily all at once) of training sessions covering First Aid/CPR, Community Building, Wilderness Skills, Risk Management, and Trip-specific outdoor experience. Leaders can get PE credit for the trainings. Croo members are also required to complete First Aid and CPR training, as well as attend Croo specific trainings. Sessions are offered throughout the spring and summer terms.</strong></p>"),
                'spring_training_ok',
                'summer_training_ok',
            ),
            Fieldset(
                'Additional Information',
                'hanover_in_fall',
                'role_preference',
            ),
            Fieldset(
                'Dietary restrictions', 
                HTML('<p>(We use this information in packing food for Trips and it will not affect your candidacy)</p>'),
                'dietary_restrictions',
                'allergen_information', 
            ), 
            Fieldset(
                'Notices',
                HTML("<p>You must agree to the following statements in order to lead a Trip or participate on a Croo. Checking each box indicates your acceptance of the conditions for your participation in DOC Trips.</p>"),
                'trippee_confidentiality',
                'in_goodstanding_with_college',
                'trainings', 
            ),
        )


class LeaderSupplementLayout(Layout):

    def __init__(self):

        super(LeaderSupplementLayout, self).__init__(
            Fieldset(
                'Application',
                HTML('<p> Download the <a href="{% if information.leader_supplement_questions %}{{ information.leader_supplement_questions.url }}{% endif %}">Trip Leader Application</a>. Thoughtfully answer the questions and upload your responses in a Word (.docx) document. <strong>Leave the original application questions in the document with your responses.</strong> Your Trip Leader application will not be considered complete until you have uploaded answers to these questions. Be sure to save your application after uploading.</p>'),
                'document',
            ),
            Fieldset(
                'Trip Leader Availability',
                Alert(content='Answers in this section will NOT be used in the scoring process',
                      dismiss=False, css_class='alert-info'),
                HTML('<p>Please indicate your availibity for each section and type of trip. <strong>Preferred</strong> means you will be most satisfied with this option; you can prefer more than one option. <strong>Available</strong> means you could do it. If you leave a choice blank it means you absolutely cannot participate on those dates or in that activity.</p>'),
                Row(
                    Div('preferred_sections', css_class='col-sm-3'),
                    Div('available_sections', css_class='col-sm-3'),
                ),
                HTML('<p> {% include "applications/triptype_modal.html" %}</p>'),
                Row(
                    Div('preferred_triptypes', css_class='col-sm-3'),
                    Div('available_triptypes', css_class='col-sm-3'),
                ),
                Field('relevant_experience', rows=4),
                Field('trip_preference_comments', rows=2),
                Field('cannot_participate_in', rows=2),
            ),
        )

class CrooSupplementLayout(Layout):

    def __init__(self):

        super(CrooSupplementLayout, self).__init__(
            Fieldset(
                'Application',
                HTML("""<p> Download the <a href="{% if information.croo_supplement_questions %}{{ information.croo_supplement_questions.url }}{% endif %}">Croo Application</a>. Thoughtfully answer the questions and upload your responses in a Word (.docx) document. <strong>Leave the original application questions in the document with your responses.</strong> Your Croo application will not be considered complete until you have uploaded answers to these questions. Scroll down and click 'Save' after uploading your answers.</p>"""),
                'document',
            ),
            Fieldset(
                'Croo Positions',
                HTML("<p>Every croo has at least one or more <strong>Safety Leads</strong> who are responsible for medical care & evacuations at their respective location (Hanover, the Grant, etc). Safety Leads are an integral part of each croo and, in addition to their medical responsibilities, are included in all other croo activities.  If you have a WFR, EMT, W-EMT, OEC, or equivalent medical certification, you are qualified to be a Safety Lead. We will prioritize people who have higher safety certifications (EMT, W-EMT) and extensive safety experience.</p>"),
                'safety_lead_willing',
                HTML("<p>Lodj Croo has two <strong>Kitchen Witches/Wizards</strong> who are responsible for ordering, preparing, and cooking all the food at the Lodj during Trips. This role includes a significant amount of responsibility and requires some additional time before Trips begins to assist in ordering all the necessary food items for the Lodj. You are eligible to be a Kitchen Witch/Wizard if you have worked at the Moosilauke Ravine Lodge during its normal operations (non-Trips).</p>"),
                'kitchen_lead_willing',
                'kitchen_lead_qualifications',
            )
        )


class CrooApplicationGradeForm(forms.ModelForm):
    """ Form for scoring Croo applications """
    class Meta:
        model = CrooApplicationGrade
        widgets = {
            'qualifications': forms.CheckboxSelectMultiple(),
            'scratchpad': forms.Textarea(attrs=dict(rows=3)),
        }

class LeaderApplicationGradeForm(forms.ModelForm):
    """ Form for scoring Leader applications """
    class Meta:
        model = LeaderApplicationGrade
        widgets = {
            'scratchpad': forms.Textarea(attrs=dict(rows=3)),
        }



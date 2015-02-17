

from django import forms
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Div, Field, MultiField, Row, Column
from bootstrap3_datetime.widgets import DateTimePicker

from applications.models import GeneralApplication, CrooSupplement, LeaderSupplement
from db.models import TripsYear
from trips.models import Section, TripType


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
            'safety_lead_willing', 'kitchen_lead_willing'
        )

    def __init__(self, *args, **kwargs):
        super(CrooSupplementForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = CrooSupplementLayout()


class SectionChoiceField(forms.ModelMultipleChoiceField):
    """
    Custom field to display section information
    """
    widget = forms.CheckboxSelectMultiple()
    
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
            'relevant_experience', 'supplement'
        )

        widgets = {
            'preferred_triptypes': forms.CheckboxSelectMultiple,
            'available_triptypes': forms.CheckboxSelectMultiple, 
            'trip_preference_comments': forms.Textarea(attrs={'rows': 2}),
            'cannot_participate_in': forms.Textarea(attrs={'rows': 2}),
            'relevant_experience': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(LeaderSupplementForm, self).__init__(*args, **kwargs)

        # restrict querysets to current trips year
        trips_year = TripsYear.objects.current()
        self.fields['preferred_sections'].queryset = Section.objects.filter(trips_year=trips_year)
        self.fields['available_sections'].queryset = Section.objects.filter(trips_year=trips_year)
        self.fields['preferred_triptypes'].queryset = self.fields['preferred_triptypes'].queryset.filter(trips_year=trips_year)
        self.fields['available_triptypes'].queryset = self.fields['available_triptypes'].queryset.filter(trips_year=trips_year)
        
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = LeaderSupplementLayout()


class ApplicationLayout(Layout):

    def __init__(self):
        
        super(ApplicationLayout, self).__init__(
                HTML('<p>Answers in this section will NOT be used in the grading process</p>'),
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
                'personal_activities',
                'feedback',
            Fieldset(
                'Trainings',
                'medical_certifications', 
                'medical_experience', 
                'peer_training',
            ),
            Fieldset(
                'Dietary restrictions', 
                HTML('<p>(We use this information in packing food for Trips and it will not affect your candidacy)</p>'),
                'dietary_restrictions',
                'allergen_information', 
            ), 
            Fieldset(
                'Notices',
                'trippee_confidentiality',
                'in_goodstanding_with_college',
                'trainings', 
                'spring_training_ok',
                'summer_training_ok',
            ),
        )


class LeaderSupplementLayout(Layout):

    def __init__(self):

        super(LeaderSupplementLayout, self).__init__(
            Fieldset(
                'Application',
                HTML('<p> Download the <a href="{{ information.leader_supplement_questions.url }}">Trip Leader Application Questions</a>. Thoughtfully answer the questions and upload your responses in a Word (.docx) document. Your Trip Leader application will not be considered complete until you have uploaded answers to these questions. </p>'),
                'supplement',
            ),
            Fieldset(
                'Trip Leader Availability',
                HTML('<p>Please indicate your availibity for each section and type of trip.</p>'),
                Row(
                    Div('preferred_sections', css_class='col-sm-3'),
                    Div('available_sections', css_class='col-sm-3'),
                ),
                HTML('<p> {% include "applications/triptype_modal.html" %}</p>'),
                Row(
                    Div('preferred_triptypes', css_class='col-sm-3'),
                    Div('available_triptypes', css_class='col-sm-3'),
                ),
                'relevant_experience',
                'trip_preference_comments',
                'cannot_participate_in',
            ),
        )

class CrooSupplementLayout(Layout):

    def __init__(self):

        super(CrooSupplementLayout, self).__init__(
            Fieldset(
                'Application',
                HTML('<p> Download the <a href="{{ information.croo_supplement_questions.url }}">Croo Application Questions</a>. Thoughtfully answer the questions and upload your responses in a Word (.docx) document. Your Croo application will not be considered complete until you have uploaded answers to these questions. </p>'),
                'document',
            ),
            Fieldset(
                'Croo Positions',
                HTML("<p>Every croo has at least one (or more) <strong>Safety Leads</strong> who are responsible for medical care & evacuations at their respective location (Hanover, the Grant, etc). Safety Leads are an integral part of each croo and, in addition to their medical responsibilities, are included in all other croo activities.  If you have a WFR, EMT, W-EMT, OEC, or equivalent medical certification, you are qualified to be a Safety Leads. We will prioritize people who have higher safety certifications (EMT, W-EMT) and extensive safety experience.</p>"),
                'safety_lead_willing',
                HTML("<p>Lodj Croo has one <strong>Kitchen Witch/Wizard</strong> who is responsible for ordering, preparing, and cooking all the food at the Lodj during Trips. This role includes a significant amount of responsibility and requires some additional time before Trips begins to assist in ordering all the necessary food items for the Lodj. You are eligible to be the Kitchen Witch/Wizard if you have worked at the Moosilauke Ravine Lodge during its normal operations (non-Trips).</p>"),
                'kitchen_lead_willing',
            )
        )

    
        

        


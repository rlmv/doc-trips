

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
            'relevant_experience': forms.Textarea(attrs={'rows': 2}),
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


class LeaderSupplementLayout(Layout):

    def __init__(self):

        super(LeaderSupplementLayout, self).__init__(
            Fieldset(
                'Leader Supplement',
                HTML('<p> Download the <a>Leader Application Supplement</a>. Thoughtfully answer the questions and upload your responses in a Word (.docx) document. Your Leader application will not be considered complete until you have uploaded answers to these questions. </p>'),
                'supplement',
            ),
            Fieldset(
                'Trip Leader Availability',
                HTML("<p>Please indicate your availibity for each section and type of trip.</p>"),
                Row(
                    Div('preferred_sections', css_class='col-sm-3'),
                    Div('available_sections', css_class='col-sm-3'),
                ),
                Row(
                    Div('preferred_triptypes', css_class='col-sm-3'),
                    Div('available_triptypes', css_class='col-sm-3'),
                ),
                'relevant_experience',
                'trip_preference_comments',
                'cannot_participate_in',
            ),
        )

    
        

        


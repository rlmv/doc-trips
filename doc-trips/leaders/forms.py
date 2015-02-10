

from django import forms
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Div, Field, MultiField, Row, Column
from crispy_forms.bootstrap import Alert

from leaders.models import LeaderApplication
from db.models import TripsYear
from trips.models import Section, TripType


class SectionChoiceField(forms.ModelMultipleChoiceField):
    """
    Custom field to display section information
    """
    widget = forms.CheckboxSelectMultiple()
    
    def label_from_instance(self, obj):

        return mark_safe(str(obj) + ' &mdash; '  + obj.date_range_str())
        

class LeaderApplicationForm(forms.ModelForm):

    # override ModelForm field defaults
    preferred_sections = SectionChoiceField(queryset=None, required=False)
    available_sections = SectionChoiceField(queryset=None, required=False)

    class Meta:
        model = LeaderApplication
        fields = ['class_year', 'gender', 'hinman_box', 'phone',
                  'from_where', 'what_do_you_like_to_study', 'tshirt_size',
                  'dietary_restrictions', 'allergen_information', 
                  'trippee_confidentiality', 'in_goodstanding_with_college',
                  'preferred_sections', 'available_sections',
                  'preferred_triptypes', 'available_triptypes',
                  'trip_preference_comments', 'cannot_participate_in',
                  'personal_activities', 'went_on_trip',
                  'applied_to_trips', 'in_hanover_this_fall', 
                  'spring_leader_training_ok', 'summer_leader_training_ok',]

        widgets = {
            'preferred_triptypes': forms.CheckboxSelectMultiple,
            'available_triptypes': forms.CheckboxSelectMultiple, 
            'dietary_restrictions': forms.Textarea(attrs={'rows': 2}),
            'allergen_information': forms.Textarea(attrs={'rows': 2}),
            'trip_preference_comments': forms.Textarea(attrs={'rows': 2}),
            'cannot_participate_in': forms.Textarea(attrs={'rows': 2}),
        }


    def __init__(self, *args, **kwargs):
        super(LeaderApplicationForm, self).__init__(*args, **kwargs)

        # restrict querysets to current trips year
        trips_year = TripsYear.objects.current()
        self.fields['preferred_sections'].queryset = Section.objects.filter(trips_year=trips_year)
        self.fields['available_sections'].queryset = Section.objects.filter(trips_year=trips_year)
        self.fields['preferred_triptypes'].queryset = self.fields['preferred_triptypes'].queryset.filter(trips_year=trips_year)
        self.fields['available_triptypes'].queryset = self.fields['available_triptypes'].queryset.filter(trips_year=trips_year)
        
        # crispy form layout:
        self.helper = FormHelper(self)
        self.helper.layout = LeaderApplicationFormLayout()
        self.helper.form_tag = False


class LeaderApplicationFormLayout(Layout):

    def __init__(self):
        super(LeaderApplicationFormLayout, self).__init__(
            Fieldset(
                'General information', 
                Alert(content='Answers in this section will NOT be used in the grading process'),
                Div(
                    Div('class_year', css_class='col-sm-3'),
                    Div('gender', css_class='col-sm-3'),
                    Div('hinman_box', css_class='col-sm-3'),
                    Div('phone', css_class='col-sm-3'),
                    Div('tshirt_size', css_class='col-sm-3'),
                    css_class='row',
                ),
                'from_where',
                'what_do_you_like_to_study',
                'personal_activities',
                Fieldset(
                    'Dietary restrictions', 
                    'dietary_restrictions',
                    'allergen_information', 
                ),
                'trippee_confidentiality',
                'in_goodstanding_with_college',
            ), 
            Fieldset(
                'Trip availibility',
                Row(
                    Div('preferred_sections', css_class='col-sm-3'),
                    Div('available_sections', css_class='col-sm-3'),
                ),
                Row(
                    Div('preferred_triptypes', css_class='col-sm-3'),
                    Div('available_triptypes', css_class='col-sm-3'),
                ),
                'trip_preference_comments',
                'cannot_participate_in',
            ),
            Fieldset(
                'Application',
                Alert(content='Answers in this section WILL be used in grading',
                      dismiss=False, css_class='alert-warning'),
                'went_on_trip', 
                'applied_to_trips', 
                'in_hanover_this_fall',
                Fieldset(
                    'Leader training', 
                    HTML("<p>If you are selected to be a DOC First-Year Trips leader, you must complete Trip Leader Training. These trainings are fun and aim to help you feel more comfortable as a leader and allow us to build Trips {{ trips_year }} together. You are required to complete these trainings in order to lead a Trip.</p><p>The training program includes 10-12 hours of training sessions (not necessarily all at once). Sessions are offered throughout the spring and summer terms. Training includes a community building session, a risk assessment session, and a wilderness skills session (which may be specific to the type of trip you are placed on and may be an overnight trip). Leader Training dates for each term will be announced in the spring and summer terms and will be posted on our schedule online.</p>"),
                    'spring_leader_training_ok', 
                    'summer_leader_training_ok', 
                ),
            ),
        )

    
        
class LeaderApplicationFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        
        super(LeaderApplicationFormHelper, self).__init__(*args, **kwargs)
        self.layout = LeaderApplicationFormLayout()
#        self.form_class = 'form-horizontal
#        self.label_class = 'col-lg-2'
#        self.field_class = 'col-lg-8'

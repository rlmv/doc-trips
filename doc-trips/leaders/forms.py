

from django import forms
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Div, Field, MultiField, Row, Column
from crispy_forms.bootstrap import Alert
from bootstrap3_datetime.widgets import DateTimePicker

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
                  'spring_leader_training_ok', 'summer_leader_training_ok',
                  'medical_certifications', 'relevant_experience',]

        widgets = {
            'preferred_triptypes': forms.CheckboxSelectMultiple,
            'available_triptypes': forms.CheckboxSelectMultiple, 
            'dietary_restrictions': forms.Textarea(attrs={'rows': 2}),
            'allergen_information': forms.Textarea(attrs={'rows': 2}),
            'trip_preference_comments': forms.Textarea(attrs={'rows': 2}),
            'cannot_participate_in': forms.Textarea(attrs={'rows': 2}),
            'personal_activities': forms.Textarea(attrs={'rows': 4}),
            'relevant_experience': forms.Textarea(attrs={'rows': 6}),
        }

        labels = {
            'preferred_triptypes': 'Preferred types of trips:',
            'available_triptypes': 'Available types of trips:',
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


DATEPICKER_OPTIONS={'format': 'MM/DD/YYYY'}

class LeaderApplicationFormWithAdminData(LeaderApplicationForm):
    """ Form used by database views for editing LeaderApplications """
    
    class Meta(LeaderApplicationForm.Meta):
        fields = LeaderApplicationForm.Meta.fields + [
            'status', 'assigned_trip', 'community_building', 
            'risk_management', 'wilderness_skills', 'first_aid']

        widgets = dict(list(LeaderApplicationForm.Meta.widgets.items()) + [
            ('community_building', DateTimePicker(options=DATEPICKER_OPTIONS)),
            ('risk_management', DateTimePicker(options=DATEPICKER_OPTIONS)),
            ('wilderness_skills', DateTimePicker(options=DATEPICKER_OPTIONS)),
            ('first_aid', DateTimePicker(options=DATEPICKER_OPTIONS)),
        ])

    def __init__(self, *args, **kwargs):
        super(LeaderApplicationFormWithAdminData, self).__init__(*args, **kwargs)
        
        # can only be assigned in the current trips year
        self.fields['assigned_trip'].queryset = (
            self.fields['assigned_trip'].queryset.filter(trips_year=TripsYear.objects.current()))
        
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            LeaderApplicationAdministrationLayout(),
            LeaderApplicationFormLayout(),
            Submit('submit', 'Update'),
        )


class LeaderApplicationAdministrationLayout(Layout):
    """ Layout for directorate's-eye's only application data """

    def __init__(self):
        super(LeaderApplicationAdministrationLayout, self).__init__(
            Fieldset(
                '',
                Row(
                    Div('status', css_class='col-sm-3'),
                    Div('assigned_trip', css_class='col-sm-3'),
                ),
                Fieldset(
                    'Trainings',
                    Row(
                        Div('community_building', css_class='col-sm-3'),
                        Div('risk_management', css_class='col-sm-3'),
                        Div('wilderness_skills', css_class='col-sm-3'),
                        Div('first_aid', css_class='col-sm-3'),
                    )
                )
            )
        )
 

class LeaderApplicationFormLayout(Layout):

    def __init__(self):
        super(LeaderApplicationFormLayout, self).__init__(
            Fieldset(
                'General information', 
                HTML('<p>Answers in this section will NOT be used in the grading process</p>'),
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
                Fieldset(
                    'Relevant experience',
                    HTML('<p>For each type of trip you are interested in leading, please describe your level of expertise and any amount of previous experience that might qualify you to lead that particular trip. Include any accomplishments, special skills, or certifications that you consider relevant (lifeguard training, yoga experience, mountain biking enthusiast, photography class, NOLS, skiing since you were a baby, etc.)</p>'), 
                    'relevant_experience',
                ),
                'trip_preference_comments',
                'cannot_participate_in',
                'medical_certifications',
                'went_on_trip', 
                'applied_to_trips', 
                'in_hanover_this_fall',
            ),
            Fieldset(
                'Dietary restrictions', 
                HTML('<p>(We use this information in packing food for Trips and it will not affect your candidacy)</p>'),
                'dietary_restrictions',
                'allergen_information', 
            ),
            Fieldset(
                'Leader training', 
                HTML("<p>If you are selected to be a DOC First-Year Trips leader, you must complete Trip Leader Training. These trainings are fun and aim to help you feel more comfortable as a leader and allow us to build Trips {{ trips_year }} together. You are required to complete these trainings in order to lead a Trip.</p><p>The training program includes 10-12 hours of training sessions (not necessarily all at once). Sessions are offered throughout the spring and summer terms. Training includes a community building session, a risk assessment session, and a wilderness skills session (which may be specific to the type of trip you are placed on and may be an overnight trip). Leader Training dates for each term will be announced in the spring and summer terms and will be posted on our schedule online.</p>"),
                'spring_leader_training_ok', 
                'summer_leader_training_ok', 
            ),
            Fieldset(
                'Disclosure',
                'trippee_confidentiality',
                'in_goodstanding_with_college',
            ),
            Fieldset(
                'Application',
                Alert(content='Answers in this section WILL be used in grading',
                      dismiss=False, css_class='alert-warning'),
            ),
        )

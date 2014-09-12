
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Div, Field, MultiField
from crispy_forms.bootstrap import Alert



class LeaderApplicationFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        
        super(LeaderApplicationFormHelper, self).__init__(*args, **kwargs)
        self.layout = LeaderApplicationLayout()
#        self.form_class = 'form-horizontal
#        self.label_class = 'col-lg-2'
#        self.field_class = 'col-lg-8'


class LeaderApplicationLayout(Layout):
    
    def __init__(self, *args, **kwargs):
        super(LeaderApplicationLayout, self).__init__(
            Fieldset(
                'General information', 
                Alert(content='Answers in this section will NOT be used in the grading process'),
                'class_year',
                'gender', 
                'hinman_box', 
                'phone', 
                'from_where', 
                'what_do_you_like_to_study',
                'tshirt_size', 
                Fieldset(
                    'Dietary restrictions', 
                    'dietary_restrictions', 
                    'allergen_information', 
                    'trippee_confidentiality', 
                ),
                'in_goodstanding_with_college',
            ), 
            Fieldset(
                'Trip availibility',
                Alert(content='Answers in this section will NOT be used in the grading process'),
                'preferred_sections',
                'available_sections',
                'preferred_triptypes',
                'available_triptypes',
                'trip_preference_comments',
            ),
            Fieldset(
                'Application',
                Alert(content='Answers in this section WILL be used in grading',
                      dismiss=False, css_class='alert-warning'),
                'personal_activities', 
                'personal_communities', 
                'went_on_trip', 
                'applied_to_trips', 
                'is_in_hanover_this_fall',
                'tell_us_about_yourself', 
                'comforting_experience', 
                'best_compliment',
                Fieldset(
                    'Thinking about First Year Trips', 
                    'trip_leader_roles',
                    'what_to_change_about_trips', 
                ), 
                Fieldset(
                    'Leadership', 
                    'leadership_experience',
                    'working_with_difference', 
                    'coleader_qualities',
                ), 
                Fieldset(
                    'Bring it all together', 
                    'why_do_you_want_to_be_involved',
                ), 
                Fieldset(
                    '', 
                    'medical_certifications',
                    'relevant_experience',
                    'cannot_participate_in', 
                ),
                Fieldset(
                    'Leader training', 
                    HTML("<p>If you are selected to be a DOC First-Year Trips leader, you must complete Trip Leader Training. These trainings are fun and aim to help you feel more comfortable as a leader and allow us to build Trips {{ trips_year }} together. You are required to complete these trainings in order to lead a Trip.</p><p>The training program includes 10-12 hours of training sessions (not necessarily all at once). Sessions are offered throughout the spring and summer terms. Training includes a community building session, a risk assessment session, and a wilderness skills session (which may be specific to the type of trip you are placed on and may be an overnight trip). Leader Training dates for each term will be announced in the spring and summer terms and will be posted on our schedule online.</p>"),
                    'spring_leader_training_ok', 
                    'summer_leader_training_ok', 
                ),
                Fieldset(
                    'Express yourself', 
                    'express_yourself', 
                ),
            ),
        )
        


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Div
from crispy_forms.bootstrap import Alert



class LeaderApplicationFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        
        super(LeaderApplicationFormHelper, self).__init__(*args, **kwargs)
        self.layout = LeaderApplicationLayout()
        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-2'
        self.field_class = 'col-lg-8'


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
                'trippee_confidentiality', 
                'in_goodstanding_with_college',
            ), 
            Fieldset(
                'Trip availibility',
                Alert(content='Answers in this section will NOT be used in the grading process'),
                'preferred_sections',
                'available_sections',
                'preferred_triptypes',
                'available_triptypes',
                HTML("<p>Looking at the Trips descriptions, please feel free to use this space to address any concerns or explain your availability. This will only be used to help us in Trip assignments, it will not be considered when your application is being read.</p>"),
                'trip_preference_comments',
            ),
            Fieldset(
                'Application',
                Alert(content='Answers in this section WILL be used in grading',
                      dismiss=False, css_class='alert-warning'),
                'personal_activities', 
                'personal_communities', 
            ),
        )
        



from django.forms import ModelForm
from django.core.urlresolvers import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from vanilla import UpdateView
from bootstrap3_datetime.widgets import DateTimePicker

from timetable.models import Timetable
from permissions.views import TimetablePermissionRequired

OPTIONS = {'format': 'MM/DD/YYYY hh:mm a'}

class TimetableForm(ModelForm):
    
    class Meta:
        model = Timetable
        widgets = {
            'leader_application_open': DateTimePicker(options=OPTIONS),
            'leader_application_closed': DateTimePicker(options=OPTIONS),
            'leader_assignment_posted': DateTimePicker(options=OPTIONS),
            'trippee_registration_open': DateTimePicker(options=OPTIONS),
            'trippee_registration_closed': DateTimePicker(options=OPTIONS),
            'trippee_assignment_posted': DateTimePicker(options=OPTIONS),
        }

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Change calendar dates'))
    

class TimetableEditView(TimetablePermissionRequired, UpdateView):
    
    model = Timetable
    form_class = TimetableForm
    template_name = 'timetable/timetable.html'
    success_url = reverse_lazy('timetable:timetable')

    def get_object(self):
        
        return Timetable.objects.timetable()
        

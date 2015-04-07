

from django.forms import ModelForm
from django.core.urlresolvers import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from vanilla import UpdateView
from bootstrap3_datetime.widgets import DateTimePicker

from doc.timetable.models import Timetable
from doc.permissions.views import TimetablePermissionRequired

OPTIONS = {'format': 'MM/DD/YYYY HH:mm'} 
# 'MM/DD/YYYY hh:mm a'} won't work without changing the 
# DATETIME_INPUT_FORMATS setting

class TimetableForm(ModelForm):
    
    class Meta:
        model = Timetable
        widgets = {
            'applications_open': DateTimePicker(options=OPTIONS),
            'applications_close': DateTimePicker(options=OPTIONS),
            'leader_assignment_posted': DateTimePicker(options=OPTIONS),
            'trippee_registrations_open': DateTimePicker(options=OPTIONS),
            'trippee_registrations_close': DateTimePicker(options=OPTIONS),
        }

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Update'))
    

class TimetableEditView(TimetablePermissionRequired, UpdateView):
    
    model = Timetable
    form_class = TimetableForm
    template_name = 'timetable/timetable.html'
    success_url = reverse_lazy('timetable:timetable')

    def get_object(self):
        
        return Timetable.objects.timetable()
        

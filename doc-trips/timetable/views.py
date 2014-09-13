

from django.forms import ModelForm
from django.core.urlresolvers import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from vanilla import UpdateView

from timetable.models import Timetable
from permissions.views import TimetablePermissionRequired

class TimetableForm(ModelForm):
    
    class Meta:
        model = Timetable

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Change calendar dates'))
    

class TimetableEditView(TimetablePermissionRequired, UpdateView):
    
    model = Timetable
    form_class = TimetableForm
    template_name = 'timetable/timetable.html'
    success_url = reverse_lazy('timetable:timetable')

    def get_object(self):
        
        return Timetable.objects.timetable()
        

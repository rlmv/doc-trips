
from vanilla import TemplateView
from braces.views import LoginRequiredMixin

from doc.timetable.models import Timetable

class VolunteerPortalView(LoginRequiredMixin, TemplateView):
    
    template_name = 'applications/portal.html'

    def get_context_data(self, **kwargs):
        
        timetable = Timetable.objects.timetable()
        return super(VolunteerPortalView, self).get_context_data(
            timetable=timetable
        )

    

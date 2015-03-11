

from vanilla import CreateView
from braces.views import LoginRequiredMixin

from doc.trippees.models import TrippeeRegistration

class Register(LoginRequiredMixin, CreateView):
    """ 
    Register for trips 
    
    """
    model = TrippeeRegistration
    template_name = 'trippees/register.html'

    def form_valid(self, form, **kwargs):
        form.instance.user = self.request.user
        return super(Register, self).form_valid(form, **kwargs)


class EditRegistration(LoginRequiredMixin, CreateView):
    """
    Edit a trippee registration.
    """
    model = TrippeeRegistration
    template_name = 'trippees/register.html'

    def get_object(self):
        return self.model.objects.filter(
            trips_year=TripsYear.objects.current(),
            user=self.request.user,
        )
            
        
    

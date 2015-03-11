
from django.core.urlresolvers import reverse_lazy
from vanilla import CreateView, UpdateView, DetailView
from braces.views import LoginRequiredMixin

from doc.trippees.models import TrippeeRegistration
from doc.trippees.forms import RegistrationForm

class Register(LoginRequiredMixin, CreateView):
    """ 
    Register for trips 
    """
    model = TrippeeRegistration
    template_name = 'trippees/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('trippees:view_registration')

    def form_valid(self, form, **kwargs):
        """ 
        Add the registering user to the registration

        The Registration creates a Trippee object automagically.
        """
        form.instance.trips_year = TripsYear.objects.current()
        form.instance.user = self.request.user
        return super(Register, self).form_valid(form, **kwargs)


class EditRegistration(LoginRequiredMixin, UpdateView):
    """
    Edit a trippee registration.
    """
    model = TrippeeRegistration
    template_name = 'trippees/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('trippees:view_registration')

    def get_object(self):
        return self.model.objects.filter(
            trips_year=TripsYear.objects.current(),
            user=self.request.user
        )
           
 
class ViewRegistration(LoginRequiredMixin, DetailView):
    """
    View a complete registration 
    """
    model = TrippeeRegistration
    template_name = 'trippees/completed_registration.html'
    fields = ['name']
    
    def get_object(self):
        return self.model.objects.filter(
            trips_year=TripsYear.objects.current(),
            user=self.request.user
        )
         
    
    
 

    

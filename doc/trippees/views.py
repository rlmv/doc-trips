
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from vanilla import CreateView, UpdateView, DetailView
from braces.views import LoginRequiredMixin

from doc.trippees.models import TrippeeRegistration
from doc.trippees.forms import RegistrationForm
from doc.db.models import TripsYear

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
        """ Get registration for user """        
        return get_object_or_404(
            self.model, user=self.request.user,
            trips_year=TripsYear.objects.current()
        )
           
 
class ViewRegistration(LoginRequiredMixin, DetailView):
    """
    View a complete registration 
    """
    model = TrippeeRegistration
    template_name = 'trippees/completed_registration.html'
    fields = ['name'] # TODO
    
    def get_object(self):
        """ Get registration for user """
        return get_object_or_404(
            self.model, user=self.request.user,
            trips_year=TripsYear.objects.current()
        )
           
         
    
    
 

    

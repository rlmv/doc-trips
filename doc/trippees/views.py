

from vanilla import CreateView
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

    def form_valid(self, form, **kwargs):
        """ 
        Add the registering user to the registration

        The Registration creates a Trippee object automagically.
        """
        form.instance.trips_year = TripsYear.objects.current()
        form.instance.user = self.request.user
        return super(Register, self).form_valid(form, **kwargs)


class EditRegistration(LoginRequiredMixin, CreateView):
    """
    Edit a trippee registration.
    """
    model = TrippeeRegistration
    template_name = 'trippees/register.html'
    form_class = RegistrationForm

    def get_object(self):
        return self.model.objects.filter(
            trips_year=TripsYear.objects.current(),
            user=self.request.user
        )
           
 
    

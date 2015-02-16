
from vanilla import CreateView
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy

from db.views import CrispyFormMixin
from applications.models import GeneralApplication


class NewApplication(LoginRequiredMixin, CrispyFormMixin, CreateView):

    model = GeneralApplication
    success_url = reverse_lazy('applications:edit_application')
    


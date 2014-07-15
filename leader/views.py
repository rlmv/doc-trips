

from django.forms import ModelForm
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required

from constance import config

from .models import LeaderApplication

import logging
logger = logging.getLogger(__name__)

class LeaderApplicationView(DetailView):
    model = LeaderApplication
    context_object_name = 'leaderapplication'
    # default form : leaderapplication_detail.html
    
leaderapplication = login_required(LeaderApplicationView.as_view())


class CreateLeaderApplication(CreateView):
    model = LeaderApplication
    fields = ['class_year', 'gender', 'tshirt_size', 'hinman_box', 'phone',
              'offcampus_address', 'notes',] 
    
    def form_valid(self, form):
        """ Attach creating user to Application. """
        form.instance.user = self.request.user
        form.instance.trips_year = config.trips_year
        return super(CreateLeaderApplication, self).form_valid(form)

    # the views uses the default form leaderapplication_form.html

create_leaderapplication = login_required(CreateLeaderApplication.as_view())

class EditLeaderApplication(UpdateView):
    model = LeaderApplication
    fields = '__all__'

edit_leaderapplication = login_required(EditLeaderApplication.as_view())



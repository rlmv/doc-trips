
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required

from constance import config

from .models import LeaderApplication

import logging
logger = logging.getLogger(__name__)

from django_easyfilters import FilterSet
class LeaderApplicationFilterSet(FilterSet):
    fields = [
        'status',
        'class_year',
    ]

from vanilla import ListView

class FilterListView(ListView):

    """ Implements easyfilter filtering on a vanilla ListView. 

    filterset and context_filter_name attributes must be specified.
    """
    
    filterset = None # filterset object
    context_filter_name = None # context name of filter
    
    def __init__(self, *args, **kwargs):
        super(FilterListView, self).__init__(*args, **kwargs)
        
        if self.filterset is None or self.context_filter_name is None:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured("FilterListView requires 'filterset' "
                                       "and 'context_filter_name' attributes")
    
    def get_queryset(self):
        qs = super(FilterListView, self).get_queryset()
        self.filter_object = self.filterset(qs, self.request.GET)
        return self.filter_object.qs

    def get_context_data(self, **kwargs):
        context = super(FilterListView, self).get_context_data(**kwargs)
        context[self.context_filter_name] = self.filter_object
        return context

        
class LeaderApplicationList(FilterListView):
    
    model = LeaderApplication
    template_name = 'leader/list_application.html'
    context_object_name = 'applications'
    filterset = LeaderApplicationFilterSet
    context_filter_name = 'application_filter'

list_view = login_required(LeaderApplicationList.as_view())
    

class LeaderApplicationView(DetailView):
    model = LeaderApplication
    context_object_name = 'leader_application'
    # default template : leaderapplication_detail.html
    
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




import logging

from django.shortcuts import render
from vanilla import TemplateView


class HomePage(TemplateView):
    """ Site landing page """
    template_name = 'index.html'


def permission_denied(request):
    """ 
    Custom 403 page. 

    Show the db navigation if we are already in the db.
    """

    if request.resolver_match.namespace.startswith('db'):
        context = {'base_template': 'db/base.html',
                   'trips_year': request.resolver_match.kwargs['trips_year']}
    else:
        context = {'base_template': 'base.html'}

    return render(request, 'permission_denied.html', context, status=403)

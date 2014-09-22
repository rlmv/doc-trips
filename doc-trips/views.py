
from django.http import HttpResponse

from vanilla import TemplateView

import logging

logger = logging.getLogger(__name__)

class HomePage(TemplateView):
    
    template_name = 'index.html'
    

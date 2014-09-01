
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

import logging

logger = logging.getLogger(__name__)

def index(request):
    return HttpResponse('Welcome to the DOC Trips website')
    

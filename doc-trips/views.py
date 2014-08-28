
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

import logging

logger = logging.getLogger(__name__)

@login_required
def index(request):
    logger.error('tests')
    return HttpResponse('hi!')
    

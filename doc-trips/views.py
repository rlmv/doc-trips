
from django.http import HttpResponse

import logging

logger = logging.getLogger(__name__)


def index(request):

    return HttpResponse('Welcome to the DOC Trips website')
    

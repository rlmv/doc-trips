
import logging
from zipfile import BadZipFile

import mammoth
import bleach
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


BLEACH_WHITELIST = {
    'tags': ['p', 'strong', 'br', 'table', 'td', 'tr', 
             'em', 'ol', 'li', 'a', 'sup'],
    'attributes': {
        'a': ['href'],
    },
    'styles': [],
}

def sanitize_html(html):

    return bleach.clean(html, **BLEACH_WHITELIST)

    
class ConversionError(Exception):
    pass


def convert_docx_to_html(file_obj):
    try:
        result = mammoth.convert_to_html(file_obj)
    except BadZipFile as exc:
        logger.info('Conversion error ' + str(exc))
        raise ConversionError(exc)
        
    html = sanitize_html(result.value)
    
    return mark_safe(html)
    

def convert_docx_filefield_to_html(filefield):

    if filefield: 
        with filefield as docx_file:
            try:
                return convert_docx_to_html(docx_file)
            except ConversionError as exc:
                return 'File Conversion Error'

    return None

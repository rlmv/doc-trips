
import logging
from zipfile import BadZipFile

import mammoth
import bleach
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


BLEACH_WHITELIST = {
    'tags': ['p', 'strong', 'br', 'table', 'td', 'tr',
             'em', 'ol', 'ul', 'li', 'a', 'sup'],
    'attributes': {
        'a': ['href'],
    },
    'styles': [],
}


def sanitize_html(html):
    """ Escape all unapproved tags from the html string """

    return bleach.clean(html, **BLEACH_WHITELIST)


class ConversionError(Exception):
    pass


def convert_docx_to_html(file_obj):
    """ 
    Convert a docx file-like object to html.

    Return a sanitized, django-safe html string, or raise a 
    ConversionError if something went wrong.
    """

    try:
        result = mammoth.convert_to_html(file_obj)
    except Exception as exc:
        logger.info('Conversion error ' + str(exc))
        raise ConversionError(exc)

    html = sanitize_html(result.value)

    return mark_safe(html)


def convert_docx_filefield_to_html(filefield):
    """
    Convert a django FileField containing a docx file to html.

    This doesn't perform a file type check. Raises a ConversionError
    if conversions fails.
    """

    # empty filefield
    if not filefield:
        return None

    with filefield as docx_file:
        return convert_docx_to_html(docx_file)

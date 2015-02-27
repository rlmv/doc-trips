
from django import template

from doc.utils.convert import convert_docx_filefield_to_html

register = template.Library()


@register.simple_tag
def display_docx_filefield_as_html(filefield):

    return convert_docx_filefield_to_html(filefield)

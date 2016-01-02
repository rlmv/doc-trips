
from django import template

from fyt.utils.convert import convert_docx_filefield_to_html, ConversionError

register = template.Library()


@register.simple_tag
def display_docx_filefield_as_html(filefield):

    if not filefield:
        return ''

    t = template.Template("""
    <div class="alert alert-info" role="alert">
    Can't see the application, or the formatting is wonky? 
    <a href="{{ filefield.url }}">Download the application here </a>
    </div>
    <div class="well">
    {{ html }}
    </div>
    """)

    try:
        html = convert_docx_filefield_to_html(filefield)
    except ConversionError:
        html = 'docx to HTML conversion failed. Try downloading the document instead.'

    c = template.Context({'filefield': filefield, 'html': html})
    return t.render(c)

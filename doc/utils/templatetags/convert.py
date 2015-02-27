
from django import template

from doc.utils.convert import convert_docx_filefield_to_html

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
    c = template.Context({'filefield': filefield, 
                          'html': convert_docx_filefield_to_html(filefield) })
    return t.render(c)

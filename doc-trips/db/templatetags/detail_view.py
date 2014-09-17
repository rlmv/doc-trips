

from django import template
from django.shortcuts import render

register = template.Library()

@register.simple_tag
def detail(db_object):

    fields = []
    
    for field in db_object._meta.fields:
        print(dir(field))
        pair = (field.verbose_name, getattr(db_object, field.name))
        fields.append(pair)
    
    t = template.loader.get_template('db/_detail_view_tag.html')
    c = template.Context({'fields': fields})
    return t.render(c)
    

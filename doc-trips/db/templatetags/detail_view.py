

from django import template
from django.shortcuts import render
from django.db import models

from db.templatetags.links import *
register = template.Library()

@register.simple_tag
def detail(db_object, fields=None):
    """ 
    Output a generic detail view of a database object.
    """
    
    if not fields:
        fields = db_object._meta.get_all_field_names()
    
    display_fields = []
    for field_name in fields:
        
        field = db_object._meta.get_field_by_name(field_name)[0]

        if field_name in ['id', 'trips_year'] or field_name.endswith('_id'):
            continue

        if isinstance(field, models.related.RelatedObject):
            continue

        value = getattr(db_object, field_name)
        
        if isinstance(field, models.ManyToManyField):
            t = template.Template(
                """
                {% for o in queryset %}
                <a href="{{ o.get_absolute_url }}"> {{ o }}</a>
                {% endfor %}
                """)
            c = template.Context({'queryset': value.get_queryset()})
            value = t.render(c)

        if isinstance(field, models.BooleanField):
            if value:
                value = "yes"
            else:
                value = "no"
            
        display_fields.append((field.verbose_name, value))
        
    t = template.loader.get_template('db/_detail_view_tag.html')
    c = template.Context({'fields': display_fields})
    return t.render(c)
    

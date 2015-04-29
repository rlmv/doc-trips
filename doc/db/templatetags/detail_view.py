

from django import template
from django.shortcuts import render
from django.db import models
from django.db.models.fields import FieldDoesNotExist

from django.contrib.auth import get_user_model
from doc.db.templatetags.links import *
register = template.Library()

@register.simple_tag
def detail(db_object, fields=None):
    """ 
    Output a generic detail view of a database object.
    
    Fields is an iterable of strings. Each string is either the
    name of a field or a method of the object. Fields can be 
    passed as (label, accessor) tuples, eg ('Section', 'get_section_name').
    """
    
    if not fields:
        fields = db_object._meta.get_all_field_names()
    
    display_fields = []
    for field_name in fields:

        # allow tuple of (name, accessor) in the field list
        if isinstance(field_name, tuple) and len(field_name) == 2:
            (label, field_name) = field_name
        else:
            label = None
            
        if field_name in ['id', 'trips_year'] or field_name.endswith('_id'):
            continue

        try:
            field = db_object._meta.get_field_by_name(field_name)[0]
            value = getattr(db_object, field_name)
        except FieldDoesNotExist:
            value = getattr(db_object, field_name)()
            if label is None:
                label = field_name
            display_fields.append((label, value))
            continue

        if isinstance(field, models.FileField) and value:
            t = template.Template("""<a href="{{ file.url }}">{{ file }}</a>""")
            c = template.Context({'file': value})
            value = t.render(c)

        if isinstance(field, models.ForeignKey):
            if isinstance(value, get_user_model()):
                # no detail views for users.
                value = str(value)

            elif value is not None:
                value = detail_link(value)

        if isinstance(field, models.related.RelatedObject):
            # related objects don't have a verbose_name
            field.verbose_name = field.get_accessor_name()
        
        if (isinstance(field, models.ManyToManyField) or 
            isinstance(field, models.related.RelatedObject)):

            t = template.Template(
                """{% for o in queryset %} <a href="{{ o.get_absolute_url }}"> {{ o }}</a>{% if not forloop.last %},{% endif %}{% endfor %}""")
            c = template.Context({'queryset': value.get_queryset()})
            value = t.render(c)

        if isinstance(field, models.BooleanField):
            if value:
                value = "yes"
            else:
                value = "no"

        if label is None:
            label = field.verbose_name
        display_fields.append((label, value))
        
    t = template.loader.get_template('db/_detail_view_tag.html')
    c = template.Context({'fields': display_fields})
    return t.render(c)
    

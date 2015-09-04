from django.db import models
from django.forms.models import modelform_factory

from doc.db.models import DatabaseModel


def make_tripsyear_formfield_callback(trips_year):
    """ 
    Return a function responsible for making formfields.
    
    Used to restrict field choices to matching trips_year.
    """
    def restrict_related_choices_by_year(model_field, **kwargs):
        """
        Formfield callback.

        If the field is a relational field, and the related object 
        is a subclass of DatabaseModel, then we only display choices 
        from the specified ``trips_year``.

        This fixes an issue where the Section dropdown for 
        /db/2014/trips/create was showing Sections objects from 2013.
        """
        formfield = model_field.formfield(**kwargs)
        if ((isinstance(model_field, models.ForeignKey) or
             isinstance(model_field, models.ManyToManyField) or
             isinstance(model_field, models.OneToOneField)) and
            issubclass(model_field.related.parent_model, DatabaseModel)):

            formfield.queryset = formfield.queryset.filter(trips_year=trips_year)

        return formfield

    return restrict_related_choices_by_year


def tripsyear_modelform_factory(model, trips_year, *args, **kwargs):
    """
    Model form factory which restricts related object choices to
    those for trips_year.

    ``formfield_callback`` is responsible for constructing a ``FormField``
    from a passed ``ModelField``. Our callback intercepts the usual ForeignKey
    implementation and restricts the queryset to objects of this ``trips_year``
    """
    callback = make_tripsyear_formfield_callback(trips_year)
    return modelform_factory(model, formfield_callback=callback, *args, **kwargs)
                             



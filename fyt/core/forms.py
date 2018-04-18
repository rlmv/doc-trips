from django.forms.models import modelform_factory
from django import forms

from fyt.core.models import DatabaseModel


def tripsyear_modelform_factory(model, *args, **kwargs):
    """
    ModelForm factory which restricts related object choices to a certain
    trips_year.
    """
    return modelform_factory(model, form=TripsYearModelForm, *args, **kwargs)


class TripsYearModelForm(forms.ModelForm):
    """
    ModelForm that restricts related object choices to the provided trips_year.

    For all fields, If the field is a relational field, and the related object
    is a subclass of DatabaseModel, then we only display choices from the
    specified ``trips_year``.
    """
    def __init__(self, data=None, files=None, trips_year=None, **kwargs):
        super().__init__(data=data, files=files, **kwargs)

        if (trips_year is not None and self.instance.pk is not None and
                trips_year != self.instance.trips_year):
            raise ValueError('Mis-matched trips_year values')

        if trips_year is not None:
            self.trips_year = trips_year
        elif self.instance.pk is not None:
            self.trips_year = self.instance.trips_year
        else:
            raise ValueError('Missing trips_year for {}. Either provide an '
                             'explicit argument, or a model instance that '
                             'has a trips_year value.'.format(
                                 self.__class__.__name__))

        for field_name, form_field in self.fields.items():
            model_field = self._meta.model._meta.get_field(field_name)

            # Since DatabaseModel manages the trips_year field, all
            # related instances are filterable
            if model_field.is_relation and issubclass(
                    model_field.related_model, DatabaseModel):
                form_field.queryset = form_field.queryset.filter(
                    trips_year=self.trips_year)

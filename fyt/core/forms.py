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
    def __init__(self, trips_year, *args, **kwargs):
        self.trips_year = trips_year

        super().__init__(*args, **kwargs)

        for field_name, form_field in self.fields.items():
            model_field = self._meta.model._meta.get_field(field_name)

            # Since DatabaseModel manages the trips_year field, all
            # related instances are filterable
            if model_field.is_relation and issubclass(
                    model_field.related_model, DatabaseModel):
                form_field.queryset = form_field.queryset.filter(
                    trips_year=trips_year)

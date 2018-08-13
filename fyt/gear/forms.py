from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from .models import GearRequest

from fyt.core.forms import TripsYearModelForm


class GearRequestForm(TripsYearModelForm):
    class Meta:
        model = GearRequest
        fields = ['gear', 'additional']
        widgets = {
            'gear': forms.CheckboxSelectMultiple(),
            'additional': forms.Textarea(attrs={'rows': 4})
        }

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        if self.instance.pk is None:
            self.instance.trips_year = self.trips_year
            self.instance.requester = user

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.add_input(Submit('submit', 'Submit'))
        return helper


class ProvidedGearForm(TripsYearModelForm):
    class Meta:
        model = GearRequest
        fields = ['provided', 'provided_comments']
        widgets = {
            'provided': forms.CheckboxSelectMultiple(),
            'provided_comments': forms.Textarea(attrs={'rows': 4})
        }

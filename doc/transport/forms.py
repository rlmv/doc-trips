
from crispy_forms.layout import Layout, Submit, Field, HTML
from crispy_forms.helper import FormHelper

from doc.transport.models import StopOrder
from django import forms


class StopOrderForm(forms.ModelForm):
    
    class Meta:
        model = StopOrder
        fields = ('trip', 'order')

    def clean_trip(self):
        """
        Really disable the stop field. There's now no
        way to update it's value.
        """
        return self.instance.trip

StopOrderFormset = forms.models.modelformset_factory(
    StopOrder, form=StopOrderForm, extra=0
)


class StopOrderFormHelper(FormHelper):
    layout = Layout(
        Field('trip', readonly=True),
        'order',
    )
    form_class = 'form-inline'

    def __init__(self, *args, **kwargs):
        super(StopOrderFormHelper, self).__init__(*args, **kwargs)
        self.add_input(Submit('submit', 'Save'))

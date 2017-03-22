
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Row, Submit
from django import forms

from fyt.transport.models import StopOrder


class StopOrderForm(forms.ModelForm):

    class Meta:
        model = StopOrder
        fields = ['order']

    trip = forms.CharField()
    stop_type = forms.CharField()
    stop = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trip'].initial = self.instance.trip
        self.fields['stop_type'].initial = self.instance.stop_type
        self.fields['stop'].initial = self.instance.stop.name


StopOrderFormset = forms.models.modelformset_factory(
    StopOrder, form=StopOrderForm, extra=0
)


class StopOrderFormHelper(FormHelper):
    layout = Layout(
        Row(
            Field('stop', readonly=True),
            Field('stop_type', readonly=True),
            Field('trip', readonly=True),
            'order',
        )
    )
    form_class = 'form-inline'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(Submit('submit', 'Save'))

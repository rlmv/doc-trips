
from crispy_forms.layout import Layout, Submit, Field, HTML
from crispy_forms.helper import FormHelper

class StopOrderFormHelper(FormHelper):
    layout = Layout(
        Field('stop', readonly=True),
        Field('distance'),
    )
    form_class = 'form-inline'

    def __init__(self, *args, **kwargs):
        super(StopOrderFormHelper, self).__init__(*args, **kwargs)
        self.add_input(Submit('submit', 'Save'))

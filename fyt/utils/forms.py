from collections import OrderedDict

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


def crispify(form, submit_text=None, css_class=None):
    """
    Add a crispy form helper and submit button to form.

    The form can then by rendered using {% crispy form %}.
    """
    if submit_text is None:
        submit_text = 'Submit'
    form.helper = FormHelper(form)
    form.helper.add_input(Submit('submit', submit_text, css_class=css_class))
    return form


class ReadonlyFormsetMixin:
    """
    A formset mixin which adds readonly information to each form in the
    formset.

    The `readonly_data` attribute controls which fields which are displayed.
    Each entry is a (name, accessor) tuple, where `name` is the string
    description of the column and `accessor` is a method on the formset.
    """

    readonly_data = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for form in self.forms:
            form.readonly_data = OrderedDict(
                [
                    (name, getattr(self, method)(form.instance))
                    for name, method in self.readonly_data
                ]
            )

    @property
    def helper(self):
        helper = FormHelper()
        # This is an overridden template in fyt/templates
        helper.template = 'bootstrap3/table_inline_formset.html'
        helper.add_input(Submit('submit', 'Save'))

        return helper

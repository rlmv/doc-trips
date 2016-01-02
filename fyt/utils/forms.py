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


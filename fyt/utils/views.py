
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from crispy_forms.helper import FormHelper


class CrispyFormMixin():
    """
    Class view mixin which adds support for crispy_forms.

    TODO: needs tests.
    """

    def get_form_helper(self, form):
        """ Return a configured crispy FormHelper. """

        return FormHelper(form)

    def get_form(self, **kwargs):
        """
        Attach a crispy form helper to the form, if it does not already have one.
        """

        form = super().get_form(**kwargs)

        if not hasattr(form, 'helper'):
            form.helper = self.get_form_helper(form)

        self.validate_crispy_layout(form)

        return form

    def validate_crispy_layout(self, form):
        """
        Validates that all fields in the form appear in the crispy layout.
        Catches a tricky bug wherein some required fields specified on the form
        are accidentally left out of an explicit layout, causing POSTS to fail.
        """

        if hasattr(form.helper, 'layout'):
            # all fields in the layout
            layout_fields = set(map(lambda f: f[1], form.helper.layout.get_field_names()))
            # and in the form
            form_fields = set(form.fields.keys())

            if form_fields - layout_fields:
                msg = ('whoa there, make sure you include ALL fields specified by '
                       '%s in the Crispy Form layout. %r are missing')
                raise ImproperlyConfigured(msg % (self.__class__.__name__, form_fields-layout_fields))


class PopulateMixin():

    def get(self, request, *args, **kwargs):
        """
        Populate the create form with data passed
        in the url querystring.
        """
        data = request.GET or None
        form = self.get_form(data=data)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class SetExplanationMixin():
    """
    Like the SetHeadline mixin.

    Exposes an 'explanation' in the template context.
    """
    explanation = None

    def get_explanation(self):
        return self.explanation

    def get_context_data(self, **kwargs):
        kwargs['explanation'] = self.get_explanation()
        return super().get_context_data(**kwargs)


class ExtraContextMixin():
    """
    A cleaner way to add to the template context.

    Instead of overridding get_context_data, implement
    a 'extra_context' method which returns a dictionary to
    update the context with.
    """
    def extra_context(self):
        return {}

    def get_context_data(self, **kwargs):
        kwargs.update(self.extra_context())
        return super().get_context_data(**kwargs)

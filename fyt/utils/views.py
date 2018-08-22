from crispy_forms.helper import FormHelper
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect


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
        if hasattr(form.helper, 'layout') and form.helper.layout is not None:
            # all fields in the layout
            layout_fields = set(map(lambda f: f[1],
                                    form.helper.layout.get_field_names()))
            # and in the form
            form_fields = set(form.fields.keys())

            missing = form_fields - layout_fields

            if missing:
                msg = ('whoa there, make sure you include ALL fields specified by '
                       '%s in the Crispy Form layout. %r are missing')
                raise ImproperlyConfigured(msg % (self.__class__.__name__, missing))


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


class MultiFormMixin():
    """
    CBV Mixin for handling multiple model forms in a single view.

    Uses the default form_valid/form_invalid (instead of a pluralized
    version) so that other mixins are compatible.
    """
    def get(self, request, *args, **kwargs):
        forms = self.get_forms(instances=self.get_instances())
        context = self.get_context_data(forms=forms)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        forms = self.get_forms(instances=self.get_instances(),
                               data=request.POST, files=request.FILES)
        if all(f.is_valid() for f in forms.values()):
            return self.form_valid(forms)

        return self.form_invalid(forms)

    def get_form_classes(self):
        raise NotImplementedError()

    def get_instances(self):
        return NotImplementedError()

    def get_forms(self, instances, **kwargs):
        """
        Return a dict mapping form names to form objects.
        """
        return {name: form_class(instance=instances.get(name), prefix=name,
                                 trips_year=self.trips_year, **kwargs)
                for name, form_class in self.get_form_classes().items()}

    def form_valid(self, forms):
        """
        Save the forms.
        """
        for form in forms.values():
            form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, forms):
        context = self.get_context_data(form_invalid=True, forms=forms)
        return self.render_to_response(context)

    def get_context_data(self, forms, **kwargs):
        return super().get_context_data(forms=forms, **kwargs)

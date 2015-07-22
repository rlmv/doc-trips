
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

        form = super(CrispyFormMixin, self).get_form(**kwargs)

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
        

class MultipleFormMixin():
    """ 
    CBV mixin for multiple forms in a view. 
   
    As written, intended for use with a ModelView. Assumes that forms 
    need to be saved. Override form_valid if not the case.
    """
    
    def get(self, request, *args, **kwargs):

        forms = self.get_forms(instances=self.get_instances())
        context = self.get_context_data(**forms)

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs): 
        
        forms = self.get_forms(instances=self.get_instances(), 
                               data=request.POST, 
                               files=request.FILES)
        
        valid = map(lambda f: f.is_valid(), forms.values())
        if all(valid):
            return self.form_valid(forms)

        return self.form_invalid(forms)

    def get_forms(self, instances=None,  **kwargs):
        
        if instances is None:
            instances = {}
            
        forms = {}
        for (name, form_class) in self.get_form_classes().items():
            forms[name] = form_class(instance=instances.get(name), 
                                     prefix=name, **kwargs)
            
        return forms

    def get_form_classes(self):
        raise ImproperlyConfigured()

    def get_instances(self):
        return {}

    def form_valid(self, forms):
        """ TODO: to make this really general, don't assume we're dealing 
        with model forms """
        for form in forms.values():
            form.save()
        
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, forms):
        
        context = self.get_context_data(**forms)
        return self.render_to_response(context)


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
        return super(SetExplanationMixin, self).get_context_data(**kwargs)


# TODO: these aren't used anywhere. Use or remove

class PassesTestMixin():

    def test_func(self):
        msg = 'Implement test_func'
        raise ImproperlyConfigured(msg)
        
    def dispatch(self, request, *args, **kwargs):
        
        if not self.test_func():
            raise PermissionDenied
        
        return super(PassesTestMixin, self).dispatch(request, *args, **kwargs)

class RedirectIfPassesTest():

    redirect_url = None
    
    def test_func(self):
        msg = 'Implement test_func'
        raise ImproperlyConfigured(msg)

    def get_redirect_url(self):
        
        if redirect_url is None:
            msg = "Add 'redirect_url' or implement 'get_redirect_url'"
            raise ImproperlyConfigurd(msg)
        
        return redirect_url

    def dispatch(self, request, *args, **kwargs):
        
        if self.test_func():
            return HttpResponseRedirect(self.get_redirect_url())
        
        return super(PassesTestMixin, self).dispatch(request, *args, **kwargs)
    

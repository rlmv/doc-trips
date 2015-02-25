
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect

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

    

    

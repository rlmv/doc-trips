
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import IntegrityError, transaction
from django.core.exceptions import NON_FIELD_ERRORS, ImproperlyConfigured
from vanilla import ListView, UpdateView, CreateView, DeleteView


class LoginRequiredMixin():
    """ Class view mixin which adds login protection """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class DatabaseMixin():
    """ Mixin for vanilla views to filter objects based on trips_year.

    Plugs into ModelViews. The url is a database url of the form
    /something/{{trips_year}}/something. The ListView will only display 
    objects for the specified trips_year.

    TODO: handle requests for trips_years which are not in the database.
    They should give 404s? This must not mess up ListViews with no results.
    """

    def get_queryset(self):
        """ Get objects for requested trips_year """

        qs = super(DatabaseMixin, self).get_queryset()
        return qs.filter(trips_year=self.kwargs['trips_year'])

    def form_valid(self, form):
        """ Called for valid forms - specifically Create and Update
 
        This deals with a corner case of form validation. Because we add 
        the current trips_year in DatabaseModel.save, which happens after
        ModelForm validation, we cannot check for uniqueness constraints 
        raised by trips_year (specifically for ScheduledTrip). Fortunately
        the databse raises an IntegrityError, which we catch here and pass to 
        form_invalid.

        TODO: parse and prettify the error message
        """

        try:
            with transaction.atomic():
                return super(DatabaseMixin, self).form_valid(form)
        except IntegrityError as e:
            form.errors[NON_FIELD_ERRORS] = form.error_class([e.__cause__])
            return self.form_invalid(form)

    @classmethod
    def urlpattern(cls):
        """ Return the default urlpattern for this view 

        Implemented on subclass, this is just an interface stub
        """
        msg = 'Not implemented. Implement urlpattern() method on {}'
        raise ImproperlyConfigured(msg.format(cls))


class DatabaseListView(DatabaseMixin, LoginRequiredMixin, ListView):

    def get_template_names(self):
        """ Get the template for the ListView """
        if self.template_name:
            return [self.template_name]
        
        # auto-generate    TODO: use super() conventions?
        template_name = '{}/{}_index.html'.format(
            self.model.get_app_name(), 
            self.model.get_reference_name()
        )
        return [template_name]
    
    @classmethod
    def urlpattern(cls):
        name = '{}_index'.format(cls.model.get_reference_name())
        return url(r'^$', cls.as_view(), name=name)
    

class DatabaseCreateView(DatabaseMixin, LoginRequiredMixin, CreateView):
    template_name = 'db/create.html'

    @classmethod
    def urlpattern(cls):
        name = '{}_create'.format(cls.model.get_reference_name())
        return url(r'^create$', cls.as_view(), name=name)


class DatabaseUpdateView(DatabaseMixin, LoginRequiredMixin, UpdateView):
    template_name ='db/update.html'

    @classmethod
    def urlpattern(cls):
        name = '{}_update'.format(cls.model.get_reference_name())
        return url(r'^(?P<pk>[0-9]+)/update', cls.as_view(), name=name)

class DatabaseDeleteView(DatabaseMixin, LoginRequiredMixin, DeleteView):
    template_name = 'db/delete.html'

    success_url_pattern = None

    def get_success_url(self):
        """ Helper method for getting the success url based on 
        succes_url_pattern. 

        CreateView and UpdateView use the models get_absolute_url
        to find the success_url. DeleteView cannot do this because the
        target object hsa been deleted.
        """

        if self.success_url_pattern:
            kwargs = {'trips_year': self.kwargs['trips_year']}
            return reverse(self.success_url_pattern, kwargs=kwargs)

        return super(DatabaseDeleteView, self).get_success_url()

    @classmethod
    def urlpattern(cls):
        name = '{}_delete'.format(cls.model.get_reference_name())
        return url(r'^(?P<pk>[0-9]+)/delete', cls.as_view(), name=name)
        

    

    



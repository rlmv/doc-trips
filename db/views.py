
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from vanilla import ListView, UpdateView, CreateView, DeleteView


class LoginRequiredMixin():
    """ Class view mixin which adds login protection """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class DatabaseMixin(LoginRequiredMixin):
    """ Mixin for vanilla views to filter objects based on trips_year.

    Plugs into ModelViews. The url is a database url of the form
    /something/{{trips_year}}/something.

    TODO: handle requests for trips_years which are not in the database.
    They should give 404s? This must not mess up ListViews with no results.
    """

    def get_queryset(self):
        """ Get objects for requested trips_year """

        qs = super(DatabaseMixin, self).get_queryset()
        return qs.filter(trips_year=self.kwargs['trips_year'])


class SuccessUrlMixin():
    """ Mixin which reverses 'success_url_pattern' to lookup success url """

    success_url_pattern = None

    def get_success_url(self):
        
        if self.success_url_pattern:
            kwargs = {'trips_year': self.kwargs['trips_year']}
            return reverse(self.success_url_pattern, kwargs=kwargs)
        
        return super(SuccessUrlMixin, self).get_success_url()


class SuccessUrlWithPkMixin():
    """ Like SuccessUrlMixin, but adds the object pk to the lookup """

    success_url_pattern = None

    def get_success_url(self):
        
        if self.success_url_pattern:
            kwargs = {'trips_year': self.kwargs['trips_year'],
                      'pk': self.object.pk }
            return reverse(self.success_url_pattern, kwargs=kwargs)

        return super(SuccessUrlMixin, self).get_success_url()


class DatabaseListView(DatabaseMixin, ListView):
    pass


class DatabaseCreateView(DatabaseMixin, SuccessUrlWithPkMixin, CreateView):
    template_name = 'db/create.html'


class DatabaseUpdateView(DatabaseMixin, SuccessUrlWithPkMixin, UpdateView):
    template_name ='db/update.html'


class DatabaseDeleteView(DatabaseMixin, SuccessUrlMixin, DeleteView):
    template_name = 'db/delete.html'


    

    




from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import IntegrityError, transaction
from django.core.exceptions import NON_FIELD_ERRORS
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
                super(DatabaseMixin, self).form_valid(form)
        except IntegrityError as e:
            form.errors[NON_FIELD_ERRORS] = form.error_class([e.__cause__])
            return self.form_invalid(form)


class DatabaseListView(DatabaseMixin, LoginRequiredMixin, ListView):
    pass
    

class DatabaseCreateView(DatabaseMixin, LoginRequiredMixin, CreateView):
    template_name = 'db/create.html'


class DatabaseUpdateView(DatabaseMixin, LoginRequiredMixin, UpdateView):
    template_name ='db/update.html'


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
        
    

class DatabaseViewFactory():

    def __init__(self, model):

        ref_name = model.get_reference_name()

        class IndexView(DatabaseListView):
            pass
        IndexView.model = model
        IndexView.template_name = '{0}/{0}_index.html'.format(ref_name)
        IndexView.context_object_name = '{}s'.format(ref_name)
        IndexView.name = '{}_index'.format(ref_name)
        self.IndexView = IndexView

        class CreateView(DatabaseCreateView):
            pass
        CreateView.model = model
        CreateView.name = '{}_create'.format(ref_name)
        self.CreateView = CreateView

        class UpdateView(DatabaseUpdateView):
            pass
        UpdateView.model = model
        UpdateView.name = '{}_update'.format(ref_name)
        self.UpdateView = UpdateView

        class DeleteView(DatabaseDeleteView):
            pass
        DeleteView.model = model
        DeleteView.success_url_pattern = 'db:{}:{}'.format(ref_name, self.IndexView.name)
        DeleteView.name = '{}_delete'.format(ref_name)
        self.DeleteView = DeleteView

    def get_urls(self):
        """ Get url patterns for views """

        urlpatterns = [
            url(r'^$', self.IndexView.as_view(), name=self.IndexView.name),
            url(r'^create$', self.CreateView.as_view(), name=self.CreateView.name),                             
            url(r'^(?P<pk>[0-9]+)/update', self.UpdateView.as_view(), name=self.UpdateView.name),
            url(r'^(?P<pk>[0-9]+)/delete', self.DeleteView.as_view(), name=self.DeleteView.name)
        ]

        return urlpatterns

        

    

    



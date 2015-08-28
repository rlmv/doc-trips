import logging

from django.db import models
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.utils.safestring import mark_safe
from django.core.exceptions import NON_FIELD_ERRORS, ImproperlyConfigured
from vanilla import (
    ListView, UpdateView, CreateView, DeleteView,
    TemplateView, DetailView, RedirectView)
from braces.views import FormInvalidMessageMixin, SetHeadlineMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, ButtonHolder

from doc.db.models import TripsYear
from doc.db.forms import tripsyear_modelform_factory
from doc.permissions.views import (
    DatabaseReadPermissionRequired, DatabaseEditPermissionRequired)
from doc.utils.views import CrispyFormMixin, SetExplanationMixin, ExtraContextMixin


logger = logging.getLogger(__name__)

FORM_INVALID_MESSAGE = "Uh oh! Looks like there's an error in the form"


class TripsYearMixin():
    """ 
    Mixin for trips_year.

    Filters objects by the trips_year named group in the url.

    Plugs into ModelViews. The url is a database url of the form
    /something/{{trips_year}}/something. The ListView will only display
    objects for the specified trips_year.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Make sure the request is for a valid trips year.
        
        Requesting trips_years that don't exist in the db will
        cause problems. Block 'em here.
        
        TODO: test cases.
        """
        trips_year = self.get_trips_year()
        if not TripsYear.objects.filter(year=trips_year).exists():
            msg = 'Trips %s does not exist in the database'
            raise Http404(msg % trips_year)

        return super(TripsYearMixin, self).dispatch(request, *args, **kwargs)

    def get_trips_year(self):
        return self.kwargs['trips_year']

    def get_queryset(self):
        """ 
        Filter objects for the trips_year of the request.
        """
        qs = super(TripsYearMixin, self).get_queryset()
        return qs.filter(trips_year=self.get_trips_year())

    def get_form_class(self):
        """ 
        Restricts the choices in foreignkey form fields to objects with the
        same trips year.

        Because we can't use an F() object in limit_choices_to.

        formfield_callback is responsible for constructing a FormField
        from a passed ModelField. Our callback intercepts the usual ForeignKey
        implementation, and only lists choices which have trips_year equal
        to the trips_year matched in the url.
        """

        if self.form_class is not None:
            msg = (
                "Specifying form_class on %s means that ForeignKey "
                "querysets will contain objects for ALL trips_years. "
                "You must explicitly restrict the querysets for these "
                "fields, or bad things will happen"
            )
            logger.warn(msg % self.__class__.__name__)
            return self.form_class
            
        if hasattr(self, 'model') and self.model is not None:
            return tripsyear_modelform_factory(
                self.model, self.kwargs['trips_year'], fields=self.fields
            )
        msg = (
            "'%s' must either define 'form_class' or 'model' "
            "Or CAREFULLY override 'get_form_class()'"
        )
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def form_valid(self, form):
        """ 
        Called for valid forms - specifically Create and Update
 
        This deals with a corner case of form validation. Uniqueness
        constraints don't get caught til the object is saved and
        raises an IntegrityError.

        We catch this error and pass it to form_invalid.

        TODO: parse and prettify the error message. Can we look at 
        object._meta.unique_together? Can we make sure it is a 
        uniqueness error?
        """
        try:
            with transaction.atomic():
                return super(TripsYearMixin, self).form_valid(form)
        except IntegrityError as e:
            form.errors[NON_FIELD_ERRORS] = form.error_class([e.__cause__])
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        """ 
        Add the trips_year for this request to the context.
        """
        context = super(TripsYearMixin, self).get_context_data(**kwargs)
        context['trips_year'] = self.get_trips_year()
        return context


class DatabaseListView(DatabaseReadPermissionRequired, ExtraContextMixin,
                       TripsYearMixin, ListView):
    pass


class DatabaseCreateView(DatabaseEditPermissionRequired, ExtraContextMixin,
                         FormInvalidMessageMixin,
                         SetExplanationMixin, SetHeadlineMixin,
                         TripsYearMixin, CrispyFormMixin, CreateView):

    template_name = 'db/create.html'
    form_invalid_message = FORM_INVALID_MESSAGE

    def get_headline(self):
        return "Add a new %s" % self.model._meta.verbose_name.title()

    def post(self, request, *args, **kwargs):
        """ 
        Add trips_year to created object.

        This is the vanilla CreateView, verbatim, with the addition
        of the trips_year.
        """
        form = self.get_form(data=request.POST, files=request.FILES)
        form.instance.trips_year_id = self.get_trips_year()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_form_helper(self, form):
        """ Add 'Create' button to crispy form. """
        helper = FormHelper(form)
        helper.add_input(Submit('submit', 'Create'))
        return helper

    def get_success_url(self):
        """ TODO: for now... """
        from doc.db.urlhelpers import reverse_detail_url
        return reverse_detail_url(self.object)


class DatabaseUpdateView(DatabaseEditPermissionRequired, ExtraContextMixin,
                         SetHeadlineMixin, FormInvalidMessageMixin, TripsYearMixin,
                         CrispyFormMixin, UpdateView):
    """
    Base view for updating an object in the database.

    If 'delete_button' is True, a link to the delete view for
    this object will be added to the form's button holder.
    """
    template_name ='db/update.html'
    form_invalid_message = FORM_INVALID_MESSAGE
    delete_button = True  # add a "Delete" button?

    def get_headline(self):
        return mark_safe("Edit %s <small> %s </small>" % (
            self.model._meta.verbose_name.title(), self.object)
        )

    def get_success_url(self):
        from doc.db.urlhelpers import reverse_detail_url
        return reverse_detail_url(self.object)

    def get_form_helper(self, form):
        """ Add Submit and delete buttons to the form. """

        from doc.db.urlhelpers import reverse_delete_url
        helper = FormHelper(form)

        buttons = [Submit('submit', 'Update')]

        if self.delete_button:
            buttons.append(
                HTML('<a href="{}" class="btn btn-danger" role="button">Delete</a>'.format(
                    reverse_delete_url(self.object)
                )))

        helper.layout.append(ButtonHolder(*buttons))
        return helper
    

class DatabaseDeleteView(DatabaseEditPermissionRequired, ExtraContextMixin,
                         SetHeadlineMixin,TripsYearMixin, DeleteView):
    template_name = 'db/delete.html'
    success_url_pattern = None

    def get_headline(self):
        return "Are you sure you want to delete %s %s?" % (
            self.object.get_model_name(), self.object
        )

    def get_success_url(self):
        """ 
        Helper method for getting the success url based on the
        succes_url_pattern property.

        CreateView and UpdateView use the models get_absolute_url
        to find the success_url. DeleteView cannot do this because the
        target object hsa been deleted.
        """
        if self.success_url_pattern:
            kwargs = {'trips_year': self.get_trips_year()}
            return reverse(self.success_url_pattern, kwargs=kwargs)
        return super(DatabaseDeleteView, self).get_success_url()

    def post(self, request, *args, **kwargs):
        """
        Warn when a foreign key is protected and the object
        cannot be deleted.
        """
        try:
            resp = super(DatabaseDeleteView, self).post(request, *args, **kwargs)
            messages.success(
                request, "Succesfully deleted {}".format(self.object)
            )
            return resp
        except models.ProtectedError as e:
            msg = (
                "Oops, you can't delete {} {} because the "
                "following objects reference it: {}."
            ).format(
                self.object._meta.model.__name__,
                self.object, e.protected_objects
            )
            messages.error(request, msg)
            return HttpResponseRedirect(request.path)


class DatabaseDetailView(DatabaseReadPermissionRequired, ExtraContextMixin,
                         TripsYearMixin, DetailView):
    template_name = 'db/detail.html'
    # Fields to display in the view. Passed in the template.
    fields = None


class DatabaseTemplateView(DatabaseReadPermissionRequired, ExtraContextMixin,
                           TripsYearMixin, TemplateView):
    pass


class DatabaseLandingPage(DatabaseTemplateView):
    """ 
    Landing page of a particular trips_year in the database

    TODO: should this display the Trips index?
    """
    template_name = 'db/landing_page.html'


class RedirectToCurrentDatabase(DatabaseReadPermissionRequired, RedirectView):
    """ 
    Redirect to the trips database for the current year.

    This view is the target of database urls.
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
       
        trips_year = TripsYear.objects.current()
        return reverse('db:landing_page', kwargs={'trips_year': trips_year.pk})


import logging

from braces.views import FormInvalidMessageMixin, SetHeadlineMixin
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Submit
from django import forms
from django.contrib import messages
from django.core.exceptions import NON_FIELD_ERRORS, ImproperlyConfigured
from django.db import IntegrityError, models, transaction
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from vanilla import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    RedirectView,
    TemplateView,
    UpdateView,
)

from . import forward
from .forms import tripsyear_modelform_factory, TripsYearModelForm
from .models import TripsYear

from fyt.permissions.views import (
    DatabaseEditPermissionRequired,
    DatabaseReadPermissionRequired,
    SettingsPermissionRequired,
)
from fyt.utils.views import (
    CrispyFormMixin,
    ExtraContextMixin,
    SetExplanationMixin,
)


logger = logging.getLogger(__name__)

FORM_INVALID_MESSAGE = "Uh oh! Looks like there's an error in the form"


class TripsYearMixin():
    """
    Mixin for ``trips_year``.

    Filters objects by the ``trips_year`` named group in the url.

    Plugs into ModelViews. The url is a database url of the form
    /something/{{trips_year}}/something. The ListView will only display
    objects for the specified trips_year.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Make sure the request is for a valid trips year.

        Requesting a ``trips_year`` that don't exist in the db will
        cause problems. Block 'em here.
        """
        try:
            self.trips_year
        except TripsYear.DoesNotExist:
            raise Http404('Trips {} does not exist in the database'.format(
                self.kwargs["trips_year"]))

        return super().dispatch(request, *args, **kwargs)

    @cached_property
    def trips_year(self):
        """
        Pull trips_year out of url kwargs.

        Note that this is a int, not a TripsYear instance.
        """
        return TripsYear.objects.get(year=self.kwargs['trips_year'])

    @cached_property
    def current_trips_year(self):
        """
        The current (most-recent) trips_year.
        """
        return TripsYear.objects.current()

    def get_queryset(self):
        """
        Filter objects for the trips_year of the request.
        """
        return super().get_queryset().filter(trips_year=self.trips_year)

    def get_form_class(self):
        """
        Restricts the choices in foreignkey form fields to objects with the
        same trips year.

        This would be straightforward if ``F()`` objects were supported
        in ``limit_choices_to``, but they're not.

        Specifying form_class on means that ForeignKey
        querysets will contain objects for ALL trips_years.
        You must explicitly restrict the querysets for these
        fields, or bad things will happen
        """
        if self.form_class is not None:
            return self.form_class

        if hasattr(self, 'model') and self.model is not None:
            return tripsyear_modelform_factory(
                self.model, fields=self.fields
            )
        msg = (
            "'%s' must either define 'form_class' or 'model' "
            "Or CAREFULLY override 'get_form_class()'"
        )
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def get_form(self, data=None, files=None, **kwargs):
        """
        Returns a form instance.
        """
        cls = self.get_form_class()

        # Pass trips_year to the form, if it expects it
        return cls(trips_year=self.trips_year, data=data, files=files,
                   **kwargs)

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
                return super().form_valid(form)
        except IntegrityError as e:
            form.errors[NON_FIELD_ERRORS] = form.error_class([e.__cause__])
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Add the trips_year for this request to the context.
        """
        context = super().get_context_data(**kwargs)
        context['trips_year'] = self.trips_year
        context['current_trips_year'] = self.current_trips_year
        context['all_trips_years'] = TripsYear.objects.all().order_by('-year')
        return context


class DatabaseListView(DatabaseReadPermissionRequired, ExtraContextMixin,
                       TripsYearMixin, ListView):
    pass


class BaseCreateView(ExtraContextMixin, FormInvalidMessageMixin,
                     SetExplanationMixin, SetHeadlineMixin, TripsYearMixin,
                     CrispyFormMixin, CreateView):

    fields = '__all__'
    template_name = 'core/create.html'
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
        form.instance.trips_year = self.trips_year
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_form_helper(self, form):
        """ Add 'Create' button to crispy form. """
        helper = FormHelper(form)
        helper.add_input(Submit('submit', 'Create'))
        return helper

    def get_success_url(self):
        return self.object.detail_url()


class DatabaseCreateView(DatabaseEditPermissionRequired, BaseCreateView):
    """Create view with default database permissions."""


class BaseUpdateView(ExtraContextMixin, SetHeadlineMixin,
                     FormInvalidMessageMixin, TripsYearMixin, CrispyFormMixin,
                     UpdateView):
    """
    Base view for updating an object in the database.

    If 'delete_button' is True, a link to the delete view for
    this object will be added to the form's button holder.
    """
    template_name = 'core/update.html'
    form_invalid_message = FORM_INVALID_MESSAGE
    delete_button = True  # add a "Delete" button?
    fields = '__all__'

    def get_headline(self):
        return mark_safe("Edit %s <small> %s </small>" % (
            self.model._meta.verbose_name.title(), self.object)
        )

    def get_success_url(self):
        return self.object.detail_url()

    def get_form_helper(self, form):
        """ Add Submit and delete buttons to the form. """

        helper = FormHelper(form)

        buttons = [Submit('submit', 'Update')]

        if self.delete_button:
            buttons.append(
                HTML('<a href="{}" class="btn btn-danger" role="button">Delete</a>'.format(
                    self.object.delete_url()
                )))

        helper.layout.append(FormActions(*buttons))
        return helper


class DatabaseUpdateView(DatabaseEditPermissionRequired, BaseUpdateView):
    """ Update view with restricted permissions. """


class BaseDeleteView(ExtraContextMixin, SetHeadlineMixin, TripsYearMixin,
                     DeleteView):
    template_name = 'core/delete.html'
    success_url_pattern = None

    def get_headline(self):
        return "Are you sure you want to delete %s %s?" % (
            self.object.model_name_lower().title(), self.object
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
            kwargs = {'trips_year': self.trips_year}
            return reverse(self.success_url_pattern, kwargs=kwargs)
        return super().get_success_url()

    def post(self, request, *args, **kwargs):
        """
        Warn when a foreign key is protected and the object
        cannot be deleted.
        """
        try:
            resp = super().post(request, *args, **kwargs)
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


class DatabaseDeleteView(DatabaseEditPermissionRequired, BaseDeleteView):
    """Database delete view with default permissions."""


class DatabaseDetailView(DatabaseReadPermissionRequired, ExtraContextMixin,
                         TripsYearMixin, DetailView):
    template_name = 'core/detail.html'
    # Fields to display in the view. Passed in the template.
    fields = None

    def get_context_data(self, **kwargs):
        kwargs['update_url'] = self.object.update_url()
        kwargs['delete_url'] = self.object.delete_url()
        return super().get_context_data(**kwargs)


class DatabaseTemplateView(DatabaseReadPermissionRequired, ExtraContextMixin,
                           TripsYearMixin, TemplateView):
    pass


class DatabaseFormView(DatabaseEditPermissionRequired, ExtraContextMixin,
                       TripsYearMixin, FormView):
    pass


class DatabaseLandingPage(DatabaseTemplateView):
    """
    Landing page of a particular trips_year in the database

    TODO: should this display the Trips index?
    """
    template_name = 'core/landing_page.html'


class RedirectToCurrentDatabase(DatabaseReadPermissionRequired, RedirectView):
    """
    Redirect to the trips database for the current year.

    This view is the target of database urls.
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return reverse('core:landing_page', kwargs={
            'trips_year': TripsYear.objects.current()})


class MigrateForward(SettingsPermissionRequired, ExtraContextMixin,
                     TripsYearMixin, FormView):
    """
    Migrate the database to the next ``trips_year`
    """
    template_name = 'core/migrate.html'
    success_url = reverse_lazy('core:current')

    @property
    def trips_year(self):
        return self.current_trips_year

    @property
    def next_year(self):
        return self.trips_year.year + 1

    def get_form(self, **kwargs):
        form = forms.Form(**kwargs)
        form.helper = FormHelper()
        form.helper.add_input(Submit(
            'submit', 'Migrate', css_class='btn-danger'))

        return form

    def extra_context(self):
        return {
            'next_year': self.next_year
        }

    def form_valid(self, form):
        forward.forward()
        messages.success(self.request,
            "Succesfully migrated the database to Trips {}".format(
                self.next_year))

        return super().form_valid(form)

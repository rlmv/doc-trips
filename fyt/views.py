from braces.views import SuperuserRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.encoding import force_text
from vanilla import TemplateView


class HomePage(TemplateView):
    """ Site landing page """
    template_name = 'index.html'


class RaiseError(LoginRequiredMixin, SuperuserRequiredMixin, TemplateView):
    """Raise an error. Used to test that Sentry error logging is enabled."""

    def dispatch(self, request, *args, **kwargs):
        raise Exception(
            "Test error. This is not a bug. Raised by {}".format(request.user))


def permission_denied(request, exception):
    """
    Custom 403 page.

    Show the db navigation if we are already in the db.
    """
    context = {
        'base_template': 'base.html',
        'exception': force_text(exception)
    }

    # Add trips_year variable to core templates that need it
    if request.path != '/db/' and request.resolver_match.namespace.startswith('db'):
        context.update({
            'base_template': 'db/base.html',
            'trips_year': request.resolver_match.kwargs['trips_year']})

    return render(request, 'permission_denied.html', context, status=403)

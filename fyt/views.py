
from braces.views import LoginRequiredMixin, SuperuserRequiredMixin
from django.shortcuts import render
from vanilla import TemplateView


class HomePage(TemplateView):
    """ Site landing page """
    template_name = 'index.html'


class RaiseError(LoginRequiredMixin, SuperuserRequiredMixin, TemplateView):
    """Raise an error. Used to test that Sentry error logging is enabled."""

    def dispatch(self, request, *args, **kwargs):
        raise Exception(
            "Test error. This is not a bug. Raised by {}".format(request.user))


def permission_denied(request):
    """
    Custom 403 page.

    Show the db navigation if we are already in the db.
    """

    if request.resolver_match.namespace.startswith('db'):
        context = {'base_template': 'db/base.html',
                   'trips_year': request.resolver_match.kwargs['trips_year']}
    else:
        context = {'base_template': 'base.html'}

    return render(request, 'permission_denied.html', context, status=403)


import logging

from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from vanilla import FormView
from braces.views import (PermissionRequiredMixin, LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin)
from django.http import HttpResponseRedirect
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Row, Column

from fyt.permissions import (directors, graders, directorate,
                             trip_leader_trainers, safety_leads)
from fyt.dartdm.forms import DartmouthDirectoryLookupField
from fyt.dartdm import lookup


logger = logging.getLogger(__name__)


class BasePermissionMixin(LoginRequiredMixin):
    """
    Utility mixin for setting up other permissions.

    >>> class SomePermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    >>>     permission_required = 'some_permission'

    Users who are not logged in are redirected to the login page.
    Authenticated users without proper permissions are shown a 403 error.

    Since this includes the LoginRequired it should go first in the MRO.
    """

    redirect_unauthenticated_users = True
    raise_exception = True


# TODO: can we set permission_required with an imported permission() call ?


class DatabaseEditPermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    permission_required = 'permissions.can_edit_db'


class DatabaseReadPermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    permission_required = 'permissions.can_view_db'


class ApplicationEditPermissionRequired(BasePermissionMixin, MultiplePermissionsRequiredMixin):
    permissions = {
        'any': (
            'permissions.can_edit_db',
            'permissions.can_edit_applications_and_assign_leaders'
        )
    }


class LeaderGraderPermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    """ Only allow access to users with permission to grade leaderapplications. """
    permission_required = 'permissions.can_grade_leader_applications'


class CrooGraderPermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    """ ONly users with permission to grade crooapplications. """
    permission_required = 'permissions.can_grade_croo_applications'


class TimetablePermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    """ Access for users allowed to edit the calendar """
    permission_required = 'permissions.can_edit_timetable'


class CreateApplicationPermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    """ Access for users allowed to create/edit croo and leader applications """
    permission_required = 'permissions.can_create_applications'


class SafetyLogPermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    """
    For users allowed to report incidents in the safety log
    """
    permission_required = 'permissions.can_report_incidents'


class GenericGroupForm(forms.Form):

    members = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    new_member = DartmouthDirectoryLookupField(required=False)

    def __init__(self, group, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.group = group
        self.fields['members'].queryset = group.user_set.all()
        self.fields['members'].initial = [u.pk for u in group.user_set.all()]

        self.fields['members'].label = 'Current ' + group.name
        self.fields['new_member'].label = 'New ' + group.name

        perms_text = ('The %s group has the following permissions: ' % group.name.capitalize() +
                      '<ul>' +
                      ''.join(['<li>{}</li>'.format(p.name) for p in group.permissions.all()]) +
                      '</ul>')

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                str(group).capitalize(),
                Row(
                    Column(
                        'members',
                        'new_member',
                        css_class='col-sm-6',
                    ),
                    Column(
                        HTML('<p>' + perms_text + '</p>'),
                        css_class='col-sm-6'),
                ),
                Submit('submit', 'Update'),
                style="padding-bottom: 2em;",
            )
        )

    def update_group_with_form_data(self):
        """
        Update the group with submitted form information.

        Should only be called once the form is cleaned.
        """

        members_list = self.cleaned_data['members']
        new_member_data = self.cleaned_data['new_member']

        if new_member_data:
            UserModel = get_user_model()
            new_member, _ = UserModel.objects.get_or_create_by_netid(
                new_member_data[lookup.NETID],
                new_member_data[lookup.NAME_WITH_YEAR]
            )

            if new_member not in members_list:
                members_list = list(members_list)
                members_list.append(new_member)

        self.group.user_set = members_list
        self.group.save()

        logger.info('Updating group %s to be %r' % (self.group, members_list))


class SetPermissions(LoginRequiredMixin, PermissionRequiredMixin, FormView):

    redirect_unauthenticated_users = True
    permission_required = 'permissions.can_set_access'
    raise_exception = True

    template_name = 'permissions/set_permissions.html'
    success_url = reverse_lazy('permissions:set_permissions')

    def get_forms(self, *args, **kwargs):
        groups = [
            directors(),
            trip_leader_trainers(),
            directorate(),
            safety_leads(),
            graders()]
        return [GenericGroupForm(group, *args, prefix=str(group), **kwargs)
                for group in groups]

    def get(self, request, *args, **kwargs):
        forms = self.get_forms()
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        forms = self.get_forms(data=request.POST)
        if all(form.is_valid() for form in forms):
            return self.form_valid(forms)

        return self.form_invalid(forms)

    def form_valid(self, forms):
        """ Save updated groups """
        for form in forms:
            form.update_group_with_form_data()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, forms):
        msg = 'Uh oh. Looks like there is an error in the form'
        messages.error(self.request, msg)
        return self.render_to_response(self.get_context_data(forms=forms))

import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Fieldset, Layout, Row, Submit
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from vanilla import FormView

from fyt.dartdm import lookup
from fyt.dartdm.forms import DartmouthDirectoryLookupField
from fyt.permissions.permissions import Group, groups


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
    raise_exception = True


class MultiplePermissionsRequiredMixin(PermissionRequiredMixin):
    """Allow access if the user has *any* of the given permissions.

    This differs from `PermissionRequiredMixin` which requires *all* given
    permissions.
    """
    def has_permission(self):
        perms = self.get_permission_required()
        return any(self.request.user.has_perm(p) for p in perms)


# TODO: can we set permission_required with an imported permission() call ?

class DatabaseEditPermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    permission_required = 'permissions.can_edit_db'


class DatabaseReadPermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    permission_required = 'permissions.can_view_db'


class SettingsPermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    """ Access for users allowed to edit database settings."""
    permission_required = 'permissions.can_edit_settings'


class ApplicationEditPermissionRequired(BasePermissionMixin,
                                        MultiplePermissionsRequiredMixin):
    permission_required = (
        'permissions.can_edit_db',
        'permissions.can_edit_applications_and_assign_leaders'
    )


class TripInfoEditPermissionRequired(BasePermissionMixin,
                                     MultiplePermissionsRequiredMixin):
    permission_required = (
        'permissions.can_edit_db',
        'permissions.can_edit_trip_info'
    )


class GraderPermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    """Users allowed to score applications."""
    permission_required = 'permissions.can_score_applications'


class GraderTablePermissionRequired(BasePermissionMixin,
                                    MultiplePermissionsRequiredMixin):
    """Users with permission to see the graders table in the database."""
    permission_required = (
        'permissions.can_view_db',
        'permissions.can_score_applications',
        'permissions.can_score_as_croo_head'
    )


class SafetyLogPermissionRequired(BasePermissionMixin, PermissionRequiredMixin):
    """
    For users allowed to report incidents in the safety log
    """
    permission_required = 'permissions.can_report_incidents'


class TrainingPermissionRequired(BasePermissionMixin,
                                 MultiplePermissionsRequiredMixin):
    """
    For users to schedule trainings and update attendance.
    """
    permission_required = (
        'permissions.can_edit_trainings',
        'permissions.can_edit_db'
    )


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = []

    members = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False)
    new_member = DartmouthDirectoryLookupField(required=False)

    def __init__(self, group, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.group = group
        self.fields['members'].queryset = group.user_set.all()
        self.fields['members'].initial = [u.pk for u in group.user_set.all()]

        self.fields['members'].label = 'Current ' + group.name
        self.fields['new_member'].label = 'New ' + group.name

    def save(self):
        """
        Update the group with submitted form information.

        Should only be called once the form is cleaned.
        """
        members = self.cleaned_data['members']
        new_member_data = self.cleaned_data['new_member']

        if new_member_data:
            UserModel = get_user_model()
            new_member, _ = UserModel.objects.get_or_create_by_netid(
                new_member_data[lookup.NETID],
                new_member_data[lookup.NAME])

            if new_member not in members:
                members = list(members)
                members.append(new_member)

        self.group.user_set.set(members)

    @property
    def helper(self):
        helper = FormHelper(self)
        helper.form_tag = False

        perms_text = ('<p>The {} group has the following permissions: '
                      '<ul>{}</ul></p>'.format(
                          self.group.name.capitalize(),
                          ''.join(['<li>{}</li>'.format(p.name)
                                   for p in self.group.permissions.all()])))

        helper.layout = Layout(
            Fieldset(
                str(self.group).capitalize(),
                Row(
                    Column(
                        'members',
                        'new_member',
                        css_class='col-sm-6',
                    ),
                    Column(
                        HTML(perms_text),
                        css_class='col-sm-6'),
                ),
                Submit('submit', 'Update'),
                style="padding-bottom: 2em;",
            )
        )
        return helper


class SetPermissions(SettingsPermissionRequired, FormView):

    template_name = 'permissions/set_permissions.html'
    success_url = reverse_lazy('permissions:set_permissions')

    def get_forms(self, *args, **kwargs):
        return [GroupForm(group, *args, prefix=str(group), **kwargs)
                for group in groups.all()]

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
            form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, forms):
        msg = 'Uh oh. Looks like there is an error in the form'
        messages.error(self.request, msg)
        return self.render_to_response(self.get_context_data(forms=forms))


import logging

from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from vanilla import TemplateView, UpdateView, FormView
from braces.views import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, HTML, Div

from permissions import directors, graders, directorate
from permissions.models import SitePermission
from dartdm.forms import DartmouthDirectoryLookupField


logger = logging.getLogger(__name__)


# TODO: can we set permission_required with an imported permission() call ?

class DatabasePermissionRequired(LoginRequiredMixin, PermissionRequiredMixin):
    """ 
    Allow access to logged in users with database-level permissions.

    These are directors, croo members, etc.
    Users who are not logged in are redirected to the login page.
    Authenticated users without proper permissions are shown a 403 error.
    """

    redirect_unauthenticated_users = True
    permission_required = 'permissions.can_access_db'
    raise_exception = True


class LeaderGraderPermissionRequired(LoginRequiredMixin, PermissionRequiredMixin):
    """ Only allow access to users with permission to grade leaderapplications. """

    redirect_unauthenticated_users = True
    permission_required = 'permissions.can_grade_leader_applications'
    raise_exception = True

class CrooGraderPermissionRequired(LoginRequiredMixin, PermissionRequiredMixin):
    """ ONly users with permission to grade crooapplications. """

    redirect_unauthenticated_users = True
    permission_required = 'permissions.can_grade_croo_applications'
    raise_exception = True


class TimetablePermissionRequired(LoginRequiredMixin, PermissionRequiredMixin):
    """ Access for users allowed to edit the calendar """
    
    redirect_unauthenticated_users = True
    permission_required = 'permissions.can_edit_timetable'
    raise_exception = True


class GenericGroupForm(forms.Form):
    
    members = forms.ModelMultipleChoiceField(queryset=None, 
                                             widget=forms.CheckboxSelectMultiple, 
                                             required=False)
    new_member = DartmouthDirectoryLookupField(required=False)

    def __init__(self, group, *args, **kwargs):
        super(GenericGroupForm, self).__init__(*args, **kwargs)

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
                HTML('<p>' + perms_text + '</p>'),
                'members',
                'new_member',
                Submit('submit', 'Update'),
                style="padding-bottom: 1em;",
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
            new_member, _ = UserModel.objects.get_by_netid(
                new_member_data['netid'],
                new_member_data['name_with_year']
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
        
        groups = [directors(), directorate(), graders()]
        return [GenericGroupForm(group, *args, prefix=str(group), **kwargs) for group in groups]
            
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
        
        messages.error(self.request, 'Uh oh. Looks like there is an error in the form.')
        return self.render_to_response(self.get_context_data(forms=forms))




       

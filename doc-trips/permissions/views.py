
import logging

from django import forms
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from vanilla import TemplateView, UpdateView, FormView
from braces.views import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import Group

from permissions import directors, graders
from permissions.models import SitePermission


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


from dartdm.forms import DartmouthDirectoryLookupField

class GroupForm(forms.Form):
    """ 
    Form for assigning users to groups. 

    Used by the SetPermissions view.
    """

    directors = forms.ModelMultipleChoiceField(queryset=None, 
                                               widget=forms.CheckboxSelectMultiple, 
                                               required=False, 
                                               label='')
    new_director = DartmouthDirectoryLookupField(required=False)
    
    graders = forms.ModelMultipleChoiceField(queryset=None, 
                                             widget=forms.CheckboxSelectMultiple, 
                                             required=False, 
                                             label='')
    new_grader = DartmouthDirectoryLookupField(required=False)

    from crispy_forms.helper import FormHelper
    from crispy_forms.layout import Layout, Submit, Fieldset, Field
    from crispy_forms.bootstrap import Alert
    helper = FormHelper()
    helper.layout = Layout(
        Fieldset('Directors',
                 Alert(content='Users in the Directors group can access and edit the database, edit the timetable, grade leader applications, and grant other users access to the database via this page. Use sparingly!', css_class='alert-warning', dismiss=False),
                 'directors',
                 'new_director'),
        Fieldset('Graders', 
                 Alert(content='Graders can grade leader applications, when available', css_class='alert-warning', dismiss=False),
                 'graders',
                 'new_grader')
    )
        
    helper.add_input(Submit('submit', 'Update permissions'))
    

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        
        self.fields['directors'].queryset = directors().user_set.all()
        self.fields['directors'].initial = [u.pk for u in directors().user_set.all()]
        self.fields['graders'].queryset = graders().user_set.all()
        self.fields['graders'].initial = [u.pk for u in graders().user_set.all()]


class SetPermissions(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    
    redirect_unauthenticated_users = True
    permission_required = 'permissions.can_set_access'
    raise_exception = True

    template_name = 'permissions/set_permissions.html'
    form_class = GroupForm
    success_url = reverse_lazy('permissions:set_permissions')

    def form_valid(self, form):
        """ 
        Save updated director and grader groups.
        
        Called with a valid form submission.
        """
        
        def _update_group_with_form_data(group, list_data_form_key, new_data_form_key):
            members_list = form.cleaned_data[list_data_form_key]
            new_data = form.cleaned_data[new_data_form_key]

            if new_data:
                UserModel = get_user_model()
                new_member, _ = UserModel.objects.get_by_netid(new_data['netid'],
                                                               new_data['name_with_year'])
                if new_member not in members_list:
                    members_list = list(members_list)
                    members_list.append(new_member)

            group.user_set = members_list
            group.save()

            logger.info('Updating group %s to be %r' % (group, members_list))


        _update_group_with_form_data(directors(), 'directors', 'new_director')
        
        _update_group_with_form_data(graders(), 'graders', 'new_grader')

        return super(SetPermissions, self).form_valid(form)
        




       

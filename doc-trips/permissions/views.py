
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


class GraderPermissionRequired(LoginRequiredMixin, PermissionRequiredMixin):
    """ Only allow access to users with permission to grade leaderapplications. """

    redirect_unauthenticated_users = True
    permission_required = 'permissions.can_grade_applications'
    raise_exception = True


from dartdm.forms import DartmouthDirectoryLookupField

class GroupForm(forms.Form):
    """ 
    Form for assigning users to groups. 

    Used by the SetPermissions view.
    """

    directors = forms.ModelMultipleChoiceField(queryset=None, 
                                               widget=forms.CheckboxSelectMultiple, 
                                               required=False)
    new_director = DartmouthDirectoryLookupField(required=False)
    
    graders = forms.ModelMultipleChoiceField(queryset=None, 
                                             widget=forms.CheckboxSelectMultiple, 
                                             required=False)

    new_grader = DartmouthDirectoryLookupField(required=False)

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        
        self.fields['directors'].queryset = directors().user_set
        self.fields['directors'].initial = [u.pk for u in directors().user_set.all()]
        self.fields['graders'].queryset = get_user_model().objects.all()
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
        
        directors_list = form.cleaned_data['directors']

        new_director_data = form.cleaned_data['new_director']
        if new_director_data:
            net_id = new_director_data['net_id']
            name = new_director_data['name_with_year']

            try:
                new_director = get_user_model().objects.get(userprofile__netid=net_id)
            except get_user_model().DoesNotExist:
                new_director = get_user_model().objects.create(username=name)
                new_director.userprofile.netid = net_id
                new_director.save()

                # is the 'new' director already in the directors list?
                if new_director not in directors_list:
                    directors_list = list(directors_list.all()) + [new_director]
            
        director_group = directors()
        director_group.user_set = directors_list
        director_group.save()

        logger.info('The director group now contains {}'.format(directors_list))

        grader_group = graders()
        grader_group.user_set = form.cleaned_data['graders']
        grader_group.save()

        logger.info('The grader group now contains {}'.format(
            form.cleaned_data['graders']))

        return super(SetPermissions, self).form_valid(form)
        




       

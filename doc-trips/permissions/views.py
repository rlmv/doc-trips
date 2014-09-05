
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


from django.forms import widgets

class NetIdLookupWidget(widgets.MultiWidget):

    def __init__(self, attrs=None):

        _widgets = [widgets.TextInput(attrs=attrs), 
                    widgets.TextInput(attrs=attrs)]

        super(NetIdLookupWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):

        """ Decompresses an initial value in to the widget fields ^^ """

        if value:
            return [value]
        return [None]

class NetIdLookupField(forms.MultiValueField):

    def __init__(self, widget=None, *args, **kwargs):

        if not widget:
            widget = NetIdLookupWidget(attrs={'class': 'lookupNetId', 'placeholder': 'Search me'})
        
        fields = (forms.CharField(), forms.CharField())
        
        super(NetIdLookupField, self).__init__(fields=fields, widget=widget, *args, **kwargs)


from django.core.exceptions import ValidationError

class DartmouthDirectoryLookupField(forms.CharField):

    def __init__(self, widget=None, attrs=None, *args, **kwargs):

        if not widget:
            attrs = attrs={'class': 'lookupNetId', 'placeholder': 'search'}
            widget = widgets.TextInput(attrs=attrs)

        super(DartmouthDirectoryLookupField, self).__init__(widget=widget, 
                                                            *args, **kwargs)
       
    def clean(self, value):
        """ 
        Ensure that the database lookup is unambiguous.

        The input value is usually the result of the client-side 
        DartDM lookup, however a user can hit 'submit' with a self-
        entered name. Because of this, and instead of trying to pass the
        look up data back to the server, we do another DartDm lookup to 
        ensure that the user is unambiguous. 

        Return a dictionary

        WAIT: this going to break, since Robert Marchman is ambiguous.
        
        """
        
        # validate required, etc.
        value = super(DartmouthDirectoryLookupField, self).clean(value)

        results = dartdm_lookup(value)

        if len(results) == 0:
            raise ValidationError('User not found')
        if len(results) == 1:
            return results[0]
        else: 
            raise ValidationError('Ambiguous results')


class GroupForm(forms.Form):
    """ 
    Form for assigning users to groups. 

    Used by the SetPermissions view.
    """

    directors = forms.ModelMultipleChoiceField(queryset=None, 
                                               widget=forms.CheckboxSelectMultiple, 
                                               required=False)
    new_director = DartmouthDirectoryLookupField(required=True)
    
    graders = forms.ModelMultipleChoiceField(queryset=None, 
                                             widget=forms.CheckboxSelectMultiple, 
                                             required=False)

    new_grader = forms.CharField(required=False)

    

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

        print(form.cleaned_data['new_director'])
        
        director_group = directors()
        director_group.user_set = form.cleaned_data['directors']
        director_group.save()

        logger.info('The director group now contains {}'.format(
            form.cleaned_data['directors']))

        grader_group = graders()
        grader_group.user_set = form.cleaned_data['graders']
        grader_group.save()

        logger.info('The grader group now contains {}'.format(
            form.cleaned_data['graders']))

        return super(SetPermissions, self).form_valid(form)
        

import requests
from django.http import JsonResponse

def dnd_lookup(request):
    """ 
    Dartmouth Name Directory connector.

    The dartdm netid lookup doesn't allow cross-site requests, 
    hence no AJAX. This view allows us to do DND lookups by acting as 
    an endpoint for typeahead.
    """
    
    try:
        query = request.GET['query']
    except KeyError:
        results = []
    else:
        results = dartdm_lookup(query)
    # setting safe=False allows us to return the JSON array
    return JsonResponse(results, safe=False) 


def dartdm_lookup(query_string):
    """ 

    TODO: catch requests library errors
    """
    payload = {'term': query_string}
    r = requests.get('http://dartdm.dartmouth.edu/NetIdLookup/Lookup', 
                     params=payload)

    return r.json()

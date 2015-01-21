

from braces.views import PermissionRequiredMixin, LoginRequiredMixin
from vanilla import FormView, UpdateView, CreateView
from django.forms.models import modelformset_factory, inlineformset_factory, model_to_dict
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseInlineFormSet
from django.core.urlresolvers import reverse_lazy, reverse
from django import forms
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from db.views import TripsYearMixin, CrispyFormMixin
from db.models import TripsYear
from croos.models import CrooApplication, CrooApplicationQuestion, CrooApplicationAnswer


class CrooApplicationAnswerForm(forms.ModelForm):

    class Meta:
        model = CrooApplicationAnswer
        widgets = {
            'question': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(CrooApplicationAnswerForm, self).__init__(*args, **kwargs)

        # Label the answer field with the question. 
        # question is passed as initial data to the form, either as a pk
        # or as an object
        question =  self.initial.get('question', None)
        if question:
            # TODO: this is not v. efficient
            if isinstance(question, int):
                question = CrooApplicationQuestion.objects.get(pk=question)
                
            self.fields['answer'].label = question.question

class CrooApplicationCreate(LoginRequiredMixin, CreateView):

    model = CrooApplication
    template_name = 'croos/crooapplication_form.html'

    success_url = reverse_lazy('croos:apply')

    def dispatch(self, request, *args, **kwargs):
        
        if self.get_queryset().filter(applicant=self.request.user, 
                                      trips_year=TripsYear.objects.current()).exists():
            return HttpResponseRedirect(reverse('croos:edit_application'))
        
        return super(CrooApplicationCreate, self).dispatch(request, *args, **kwargs)

    def get_form(self, data=None, files=None, **kwargs):

        trips_year = TripsYear.objects.current()
        questions = CrooApplicationQuestion.objects.filter(trips_year=trips_year)

        if data is not None:
            # POST
            initial = None
        else: 
            # GET. Instantiate blank application and answsers
            initial = list(map(lambda q: {'answer': '', 'question': q}, questions))  

        ApplicationFormset = inlineformset_factory(CrooApplication,
                                                   CrooApplicationAnswer, 
                                                   form=CrooApplicationAnswerForm,
                                                   max_num=len(questions))
        form = ApplicationFormset(data, initial=initial)

        # TODO: move this external - attach to formset, somehow?
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit', 'Submit'))

        return form

    def form_valid(self, form):

        application = CrooApplication.objects.create(
            applicant=self.request.user, 
            trips_year=TripsYear.objects.current())
        form.instance = application
        
        return super(CrooApplicationCreate, self).form_valid(form)

        

class CrooApplicationView(LoginRequiredMixin, CrispyFormMixin, UpdateView):
    """
    Application page.
    
    This needs to reject users if the application is closed.

    No related items are selected in the app so we don't need to use the 
    tripsyear_modelform_factory. However, watch out if that changes!
    """
    model = CrooApplication
    template_name = 'croos/crooapplication_form.html'

    # TODO: add static detail page/"thanks for applying" landing page
    success_url = reverse_lazy('croos:edit_application')

    def get_object(self):
        
        return get_object_or_404(self.model, 
                                 applicant=self.request.user, 
                                 trips_year=TripsYear.objects.current())

    def get_form(self, data=None, files=None, **kwargs):
        trips_year = TripsYear.objects.current()

        ApplicationFormset = inlineformset_factory(CrooApplication, 
                                                   CrooApplicationAnswer, 
                                                   form=CrooApplicationAnswerForm,                                                      extra=0)

        form = ApplicationFormset(instance=self.object)

        # TODO: move this external - attach to formset, somehow?
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit', 'Submit'))

        return form
        
"""
Grading portal, redirects to next app to grade. 

Restricted to directorate.
"""


""" 
Grade form - read and input. 

Redirect to grading portal on successful post.
"""


"""
Create/edit this year's application.

Used by directors to edit application questions. 
SHOULD be hidden once the application is open.
"""

class CreateCrooApplication(LoginRequiredMixin, PermissionRequiredMixin, TripsYearMixin, FormView):
    
    permission_required = 'permission.can_create_croo_application'
    redirect_unauthenticate_users = True
    raise_exception = True 

    def get_form_class(self):
        
        return modelformset_factory(CrooApplicationQuestion)

    def get_form(self, data=None, files=None, **kwargs):
        
        FormClass = self.get_form_class()

        return FormClass(data, files, **kwargs)


"""
Database views of croo apps

INdex view - sortable by safety dork/croo type.
How does croo selection work? Is it blind? 

Each app should have a link to the app's grading page. Should there be a way to 
add an app back into the blind grading pool?

Directorate (directors?) can approve applications/assign them to croos. 

Access/permissions page can link to here for removing/adding to the 'Croo' group.

"""




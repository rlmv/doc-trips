

from braces.views import PermissionRequiredMixin, LoginRequiredMixin
from vanilla import FormView, UpdateView, CreateView, RedirectView, TemplateView
from django.forms.models import modelformset_factory, inlineformset_factory, model_to_dict
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseInlineFormSet, ModelForm
from django.core.urlresolvers import reverse_lazy, reverse
from django import forms
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field


from doc.db.forms import doc.tripsyear_modelform_factory
from doc.db.views import TripsYearMixin, DatabaseListView, DatabaseUpdateView, DatabaseDetailView, DatabaseDeleteView, DatabaseCreateView
from doc.db.views import PassesTestMixin
from doc.db.views import CrispyFormMixin
from doc.db.models import TripsYear
from doc.croos.models import CrooApplication, CrooApplicationQuestion, CrooApplicationAnswer, Croo, _CrooApplicationGrade as CrooApplicationGrade
from doc.permissions.views import CrooGraderPermissionRequired
from doc.timetable.models import Timetable


class CrooApplicationAnswerForm(forms.ModelForm):

    class Meta:
        model = CrooApplicationAnswer
        widgets = {
            'question': forms.HiddenInput(),
            'answer': forms.Textarea(attrs={'rows': 7})
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


class IfCrooApplicationAvailable():
    
    def dispatch(self, request, *args, **kwargs):
        
        if Timetable.objects.timetable().crooapplication_available():
            return super(IfCrooApplicationAvailable, self).dispatch(request, *args, **kwargs)
            
        return render(request, 'croos/not_available.html')
            

class NewCrooApplication(LoginRequiredMixin, IfCrooApplicationAvailable, CreateView):

    model = CrooApplication
    template_name = 'croos/crooapplication_form.html'

    success_url = reverse_lazy('croos:apply')

    def dispatch(self, request, *args, **kwargs):
        """ 
        Redirect to edit CrooApplication for this user, if user
        has already applied. 
        """
        if self.model.objects.filter(applicant=self.request.user, 
                                     trips_year=TripsYear.objects.current()).exists():
            return HttpResponseRedirect(reverse('croos:edit_application'))
        
        return super(NewCrooApplication, self).dispatch(request, *args, **kwargs)

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
                                                   extra=len(questions),
                                                   can_delete=False)
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
        
        return super(NewCrooApplication, self).form_valid(form)

        

class EditCrooApplication(LoginRequiredMixin, IfCrooApplicationAvailable, UpdateView):
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

        ApplicationFormset = inlineformset_factory(CrooApplication, 
                                                   CrooApplicationAnswer, 
                                                   form=CrooApplicationAnswerForm, 
                                                   extra=0, 
                                                   can_delete=False)

        form = ApplicationFormset(data, instance=self.object)

        # TODO: move this external - attach to formset, somehow?
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit', 'Submit'))

        return form


class CrooApplicationQuestionForm(forms.ModelForm):

    class Meta:
        model = CrooApplicationQuestion
        widgets = {
            'question': forms.Textarea(attrs={'rows': 4})
        }

class CreateCrooApplication(LoginRequiredMixin, PermissionRequiredMixin, FormView):

    """
    Create/edit this year's application.

    Used by directors to edit application questions. 

    TODO: SHOULD be hidden once the application is open.
    TODO: shrink the text field question boxes.
    """

    permission_required = 'permission.can_create_croo_application'
    redirect_unauthenticate_users = True
    raise_exception = True 

    success_url = reverse_lazy('croos:create_application')
    template_name = 'croos/create_crooapplication.html'

    def get_form(self, data=None, files=None, **kwargs):
        
        FormSet = modelformset_factory(CrooApplicationQuestion, 
                                       form=CrooApplicationQuestionForm)
        trips_year = TripsYear.objects.current()
        queryset = CrooApplicationQuestion.objects.filter(trips_year=trips_year)
        form = FormSet(data, queryset=queryset)
        
        # TODO: move this elsewhere.
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit', 'Update'))
        
        return form

    def form_valid(self, form):
        form.save()
        return super(CreateCrooApplication, self).form_valid(form)



class RedirectToNextGradableCrooApplication(CrooGraderPermissionRequired, 
                                            RedirectView):
    """ 
    Grading portal, redirects to next app to grade. 
    Identical to the corresponding LeaderGrade view 

    Restricted to directorate members.
    """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """ Redirect to next CrooApplication which needs grading """
        
        application = CrooApplication.objects.next_to_grade(self.request.user)
        if not application:
            return reverse('croos:no_applications')
        return reverse('croos:grade', kwargs={'pk': application.pk})

class CrooApplicationGradeForm(ModelForm):

    class Meta:
        model = CrooApplicationGrade
        fields = ['grade', 'comments']
        
    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit Grade'))

class GradeCrooApplication(CrooGraderPermissionRequired, CreateView):

    model = CrooApplicationGrade
    form_class = CrooApplicationGradeForm
    template_name = 'croos/grade.html'

    success_url = reverse_lazy('croos:grade_next')

    def get_context_data(self, **kwargs):
        
        context = super(GradeCrooApplication, self).get_context_data(**kwargs)
        # only grade applications from this year
        context['application'] = get_object_or_404(CrooApplication, 
                                                   trips_year=TripsYear.objects.current())
        return context

    def form_valid(self, form):
        
        form.instance.grader = self.request.user
        form.instance.application = get_object_or_404(CrooApplication, 
                                                      trips_year=TripsYear.objects.current())
        form.save()
        
        return super(GradeCrooApplication, self).form_valid(form)
        
    
class NoCrooApplicationsLeftToGrade(CrooGraderPermissionRequired, TemplateView):
    
    template_name = 'croos/no_applications.html'


"""
Database views of croo apps

INdex view - sortable by safety dork/croo type.
How does croo selection work? Is it blind? 

Each app should have a link to the app's grading page. Should there be a way to 
add an app back into the blind grading pool?

Directorate (directors?) can approve applications/assign them to croos. 

Access/permissions page can link to here for removing/adding to the 'Croo' group.

"""

class CrooApplicationDatabaseListView(DatabaseListView):
    model = CrooApplication
    context_object_name = 'crooapplications'
    template_name = 'croos/crooapplication_index.html'

class CrooApplicationDatabaseDetailView(DatabaseDetailView):
    model = CrooApplication
    context_object_name = 'crooapplication'
    template_name = 'croos/crooapplication_detail.html'

class CrooApplicationDatabaseUpdateView(DatabaseUpdateView):
    model = CrooApplication
    template_name = 'croos/crooapplication_update.html'
    
    fields = ['status', 'assigned_croo', 'potential_croos', 
              'safety_dork_qualified', 'safety_dork']

    def get_form_class(self):
        """ Use checkbox for potential croos """

        widgets = {
            'potential_croos': forms.CheckboxSelectMultiple,
        }
        return tripsyear_modelform_factory(self.model, self.kwargs['trips_year'],
                                           fields=self.fields, widgets=widgets)

    def get_form_helper(self, form):

        helper = FormHelper(form)
        helper.layout = Layout(
            'status', 
            'assigned_croo',
            'potential_croos',
            'safety_dork_qualified', 
            'safety_dork'
        )
        helper.add_input(Submit('submit', 'Update'))
        return helper


class CrooListView(DatabaseListView):
    model = Croo
    template_name = 'croos/croo_index.html'
    context_object_name = 'croos'

class CrooCreateView(DatabaseCreateView):
    model = Croo

class CrooDetailView(DatabaseDetailView):
    model = Croo
    
class CrooUpdateView(DatabaseUpdateView):
    model = Croo

class CrooDeleteView(DatabaseDeleteView):
    model = Croo
    success_url_pattern = 'db:croo_index'

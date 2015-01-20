

from braces.views import PermissionRequiredMixin, LoginRequiredMixin
from vanilla import FormView, UpdateView
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse_lazy
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from db.views import TripsYearMixin, CrispyFormMixin
from db.models import TripsYear
from croos.models import CrooApplication, CrooApplicationQuestion, CrooApplicationAnswer


class CrooApplicationAnswerForm(forms.ModelForm):

    class Meta:
        model = CrooApplicationAnswer


class CrooApplicationForm(forms.ModelForm):

    class Meta:
        model = CrooApplication
        
    def __init__(self, questions, *args, **kwargs):
        """ questions are CrooApplicationQuestions """
        super(CrooApplicationForm, self).__init__(*args, **kwargs)
        for i, question in enumerate(questions):
            self.fields['question%d' % i] = forms.CharField()

        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))


class CrooApplicationView(LoginRequiredMixin, CrispyFormMixin, UpdateView):
    """
    Application page.
    
    This needs to reject users if the application is closed.

    No related items are selected in the app so we don't need to use the 
    tripsyear_modelform_factory. However, watch out if that changes!
    """
    model = CrooApplication
    form_class = CrooApplicationForm
    template_name = 'croos/crooapplication_form.html'

    # TODO: add static detail page/"thanks for applying" landing page
    success_url = reverse_lazy('croos:apply')

    def get_object(self):
        
        try:
            return self.get_queryset().get(applicant=self.request.user, 
                                           trips_year=TripsYear.objects.current())
        except self.model.DoesNotExist:
            return None

    def get_form(self, data=None, files=None, **kwargs):
        trips_year = TripsYear.objects.current()
        
        if kwargs['instance'] is None:
            # user has not applied yet. Instantiate blank application and answsers
            application, created = CrooApplication.objects.get_or_create(applicant=self.request.user)
            questions = CrooApplicationQuestion.objects.filter(trips_year=trips_year)
            for question in questions:
                blank_answer = CrooApplicationAnswer(trips_year=trips_year, 
                                                     question=question)
                application.answers.add(blank_answer)
                blank_answer.save()
        
            application.save()

        ApplicationFormset = modelformset_factory(CrooApplicationAnswer, 
                                                  form=CrooApplicationAnswerForm)
        form = ApplicationFormset(queryset=CrooApplicationAnswer.objects.filter(application__applicant=self.request.user, trips_year=trips_year))
        return form
                        
        
    def form_valid(self, form):
        if self.object is None: # newly created
            form.instance.applicant = self.request.user
            form.instance.trips_year = TripsYear.objects.current()
        return super(CrooApplicationView, self).form_valid(form)


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




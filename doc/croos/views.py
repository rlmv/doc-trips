

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


from doc.db.forms import tripsyear_modelform_factory
from doc.db.views import TripsYearMixin, DatabaseListView, DatabaseUpdateView, DatabaseDetailView, DatabaseDeleteView, DatabaseCreateView
from doc.db.views import CrispyFormMixin
from doc.db.models import TripsYear
from doc.croos.models import CrooApplication, CrooApplicationQuestion, CrooApplicationAnswer, Croo, _CrooApplicationGrade as CrooApplicationGrade
from doc.permissions.views import CrooGraderPermissionRequired
from doc.timetable.models import Timetable


class CrooListView(DatabaseListView):
    model = Croo
    template_name = 'croos/croo_index.html'
    context_object_name = 'croos'


class CrooCreateView(DatabaseCreateView):
    model = Croo


class CrooDetailView(DatabaseDetailView):
    model = Croo
    fields = ['name', 'description', 'croo_members']

    
class CrooUpdateView(DatabaseUpdateView):
    model = Croo


class CrooDeleteView(DatabaseDeleteView):
    model = Croo
    success_url_pattern = 'db:croo_index'

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from fyt.core.forms import TripsYearModelForm
from fyt.raids.models import Comment


class CommentForm(TripsYearModelForm):

    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 2})
        }

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Comment'))

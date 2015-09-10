from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from fyt.raids.models import Comment


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 2})
        }

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Comment'))

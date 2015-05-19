
from django import forms
from django.utils.safestring import mark_safe


class SectionChoiceField(forms.ModelMultipleChoiceField):
    """ Custom form field to display the dates of Sections. """

    def label_from_instance(self, obj):
        return mark_safe(obj.name + ' &mdash; '  + obj.date_range_str())

from django import forms


class TripChoiceField(forms.ModelChoiceField):
    """
    Field with verbose Trip labels .
    """

    def label_from_instance(self, obj):
        return "{}{}: {}: {}".format(
            obj.section.name,
            obj.template.name,
            obj.template.triptype.name,
            obj.template.description_summary,
        )

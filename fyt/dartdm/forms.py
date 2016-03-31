import logging

from django import forms
from django.core.exceptions import ValidationError

from fyt.dartdm import lookup

logger = logging.getLogger(__name__)


class DartmouthDirectoryLookupWidget(forms.MultiWidget):
    """
    Widget to perform an AJAX Dartmouth name directory lookup.

    Contains one visible input field and two hidden input fields.

    TODO: save nameWithYear in the other hidden field instead of the affil?
    That will make it easier to  tell whether the autocompleted field was
    changed.
    """

    class Media:
        js = ('dartdm/lookup.js',)

    def __init__(self, attrs=None):
        widgets = [
            forms.TextInput(attrs={'class': 'dartdmLookup nameWithYearField'}),
            forms.HiddenInput(attrs={'class': 'netIdField'}),
            forms.HiddenInput(attrs={'class': 'nameWithAffilField'})]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        """
        Decompresses an initial value in to the widget fields.
        """
        # TODO:
        if value:
            return [value]
        return [None]


class DartmouthDirectoryLookupField(forms.MultiValueField):
    """
    Form field to perform a lookup in the Dartmouth Directory Manager.

    A cleaned field of this type will be a dictionary of { ____ }.

    Note: the MultiValueField takes care of validating required fields.
    """

    def __init__(self, *args, **kwargs):
        fields = (forms.CharField(), forms.CharField(), forms.CharField())
        widget = DartmouthDirectoryLookupWidget()
        super().__init__(fields=fields, widget=widget, *args, **kwargs)

    def compress(self, data_list):
        """
        Compress data from the hidden input fields.

        The input value is usually the result of the client-side DartDM lookup,
        however a user can hit 'submit' with a self-entered name, or change the
        autocompleted name. If this is the case we do another DartDm lookup to
        verify the name.

        `data_list` is of the form `[NAME_WITH_YEAR, NETID, NAME_WITH_AFFIL]`
        """
        logger.info('compress: %r' % data_list)

        if len(data_list) == 0:
            # Empty field
            return None

        if len(data_list) == 1 or not data_list[2].startswith(data_list[0]):
            # User did not wait for the typeahead autocomplete,
            # or changed the autocompleted name after the lookup.
            # Try and lookup the given name.
            results = lookup.dartdm_lookup(data_list[0])
            if len(results) == 0:
                raise ValidationError('User not found')
            elif len(results) == 1:
                return results[0]  # Lookup results are already formatted
            else:
                raise ValidationError("Ambiguous name %r" % data_list[0])

        return {
            lookup.NAME_WITH_YEAR: data_list[0],
            lookup.NETID: data_list[1],
            lookup.NAME_WITH_AFFIL: data_list[2]
        }

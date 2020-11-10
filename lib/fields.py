"""
Custom Django Fields
"""
import ast

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class PossiblyAbsentOrBlankCharField(forms.CharField):
    """
    Used for char field that can be blank or absent, if it's blank, we still want that the field
    update his value.
    """
    description = "A CharField which isn't required and will return None if absent."
    empty_values = (None, [], (), {})

    def __init__(self, *args, **kwargs):
        kwargs['required'] = False
        kwargs['empty_value'] = None
        super().__init__(*args, **kwargs)


class TagsField(forms.CharField):
    """
    Used for tags field. The initial value is a string - e.i. u'['a', 'b', 'c']' - so we first need
    to parse it using ast.literal_eval, then return a list.
    """
    description = "Used for tags field. It parses a string into a list."
    empty_values = (None, [], (), {})
    default_error_messages = {
        'invalid_list': _('Enter a list of values.'),
    }

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, str):
            value = ast.literal_eval(value)
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['invalid_list'], code='invalid_list')
        return [str(val).lower() for val in value]

    def __init__(self, *args, **kwargs):
        kwargs['required'] = False
        kwargs['empty_value'] = None
        super().__init__(*args, **kwargs)

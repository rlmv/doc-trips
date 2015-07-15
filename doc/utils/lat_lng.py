import re

from django.core.exceptions import ValidationError

LAT_LNG_REGEX = re.compile(r'((-?\d+.\d+), ?(-?\d+.\d+))')

def parse_lat_lng(string):
    match = LAT_LNG_REGEX.search(string)
    if match:
        return match.expand(r'\2,\3')

def validate_lat_lng(string):
    """
    Validator for lat/lng coords.

    Raises a ValidationError if the string
    does not match LAT_LNG_REGEX. 
    """
    string = string.strip()
    if string:
        match = LAT_LNG_REGEX.search(string)
        if not match or match.group(0) != string:
            raise ValidationError('Value must look like 43.7030,-72.2895')

import re

from django.core.exceptions import ValidationError

LAT_LNG_PARSER = re.compile(r'(-?\d+.\d+)[ ,] *(-?\d+.\d+)')
LAT_LNG_TARGET = re.compile(r'(-?\d+.\d+,-?\d+.\d+)')

def parse_lat_lng(string):
    """ 
    Try and pull something which looks like geo 
    coordinates from string.
    """
    match = LAT_LNG_PARSER.search(string)
    if match:
        return match.expand(r'\1,\2')

def validate_lat_lng(string):
    """
    Validator for lat/lng coords.

    Raises a ValidationError if the string
    does not match LAT_LNG_TARGET.
    """
    string = string.strip()
    if string:
        match = LAT_LNG_TARGET.search(string)
        if not match or match.group(0) != string:
            raise ValidationError('Value must look like 43.7030,-72.2895')

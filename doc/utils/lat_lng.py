import re

LAT_LNG_REGEX = re.compile(r'(-?\d+.\d+), ?(-?\d+.\d+)')

def parse_lat_lng(string):
    match = LAT_LNG_REGEX.search(string)
    if match:
        return match.expand(r'\1,\2')

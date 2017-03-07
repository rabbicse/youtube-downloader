import re

__author__ = 'rabbi'


def search_pattern_single(pattern, text):
    try:
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match and len(match.groups()) > 0:
            return match.group(1)
    except Exception as x:
        print(x)
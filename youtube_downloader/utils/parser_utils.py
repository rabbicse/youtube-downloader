__author__ = 'rabbi'

from urllib import parse


def unquote_url(text):
    return parse.unquote(text, encoding='utf-8')
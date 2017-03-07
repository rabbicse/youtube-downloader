# -*- coding: utf-8 -*-


from urllib import parse
import xml.etree.ElementTree as ET

__author__ = 'rabbi'

"""
ref: https://gist.github.com/YungSang/2752897
"""


def unquote_url(text):
    return parse.unquote(text, encoding='utf-8')


def format_srt_time(srt_time):
    """Convert a time in seconds (google's transcript) to srt time format."""
    try:
        sec, micro = divmod(int(srt_time), 1000)
        m, s = divmod(int(sec), 60)
        h, m = divmod(m, 60)
        return "{:02}:{:02}:{:02},{:03}".format(h, m, s, micro)
    except Exception as x:
        print('Error format str:')
        print(x)


def convert_html(text):
    """A few HTML encodings replacements.
    &amp;#39; to '
    &amp;quot; to "
    """
    return text.replace('&amp;#39;', "'").replace('&amp;quot;', '"')


def convert_srt_line(i, elms):
    """Print a subtitle in srt format."""
    start_time = float(elms[0]) * 1000
    duration = float(elms[1]) * 1000
    end_time = start_time + duration
    return "{}\n{} --> {}\n{}\n\n".format(i, format_srt_time(start_time), format_srt_time(end_time),
                                          convert_html(elms[2]))


def convert_xml_to_srt_file(text, srt_file):
    try:
        with open(srt_file, 'w', encoding='utf-8') as outfile:
            root = ET.fromstring(text)
            i = 1
            for child in root.iter('text'):
                attr_cc = child.attrib
                start = attr_cc['start']
                dur = attr_cc['dur']
                cc_text = child.text
                outfile.write(convert_srt_line(i, (start, dur, cc_text)))
                i += 1
    except Exception as x:
        print('print when parse xml')
        print(x)

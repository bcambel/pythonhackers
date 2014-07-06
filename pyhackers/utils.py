# -*- coding: utf-8 *-*
import markdown2
from os import listdir
from os.path import join, isfile
from datetime import datetime as dt, timedelta

rules = [(10 ** 9, 'B'), (10 ** 6, 'M'), (10 ** 3, 'K')]


def unix_time(date, float=False):
    epoch = dt.utcfromtimestamp(0)
    delta = date - epoch
    if float:
        return delta.total_seconds()
    else:
        return int(delta.total_seconds())


def unix_time_millisecond(date):
    """
    Uses unix_time function and multiplies with 1000 to get millisecond precision
    Epoch + millisecond precision
    :param date:
    :return:
    """
    return unix_time(date, float=True) * 1e3


def format_date(date):
    return date.strftime('%Y-%m-%d %H:%M:%S') if date is not None else ""


def time_with_ms(date):
    return date.strftime('%H:%M:%S.%f') if date is not None else ""


def epoch_to_date(milliseconds):
    seconds = milliseconds / 1000

    return (dt.utcfromtimestamp(seconds) + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")


def nice_number(n):
    numeric = n
    abbreviation = ""

    for number, abbr in rules:
        if n > number:
            abbreviation = abbr
            ident = (n * 10 / number) / 10.0
            break

    ident_int = int(ident)
    if numeric - ident_int == 0:
        numeric = ident_int

    return u"{}{}".format(numeric, abbreviation)


def files_in(directory):
    for f in listdir(directory):
        if isfile(join(directory, f)):
            yield join(directory, f)
    return


def markdown_to_html(txt):
    try:
        html_text = markdown2.markdown(txt, extras=['fenced-code-blocks'])
        return html_text.encode('ascii', 'xmlcharrefreplace').replace("codehilite", "syntax")
    except:
        return txt

if __name__ == "__main__":

    def tests():
        assert "10K" == nice_number(10020)
        assert "102" == nice_number(102)
        assert "1M" == nice_number(1002000)
        assert "1.1B" == nice_number(1102000000)

    tests()
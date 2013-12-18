# -*- coding: utf-8 *-*
from datetime import datetime as dt, timedelta


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
    return date.strftime('%Y-%m-%dT%H:%M:%S') if date is not None else ""


def time_with_ms(date):
    return date.strftime('%H:%M:%S.%f') if date is not None else ""


def epoch_to_date(milliseconds):
    seconds = milliseconds / 1000

    return (dt.utcfromtimestamp(seconds) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")


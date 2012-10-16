from datetime import date, datetime, time as dtime, timedelta
from logging import getLogger
from time import strptime, strftime, gmtime
from calendar import timegm, Calendar, weekday

logger = getLogger('common.utils.date')
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


##
# Converts the facebook date in format "mm/dd/yyyy" to DB format "yyyy-mm-dd".
# @param date A date string to convert.
# @param format The format of the date string.
# @return A date object.
def convert_datestring_format(datestring, format="%m/%d/%Y"):
    if datestring:
        try:
            value = strptime(datestring, format)
            return strftime('%Y-%m-%d', value)
        except ValueError:
            logger.exception('failed to handle DOB string=%s' % datestring)
    return None


def convert_datestring_to_datetime(datestring, format=DATETIME_FORMAT):
    """Converts a datestring to a datetime object"""
    time_struct = strptime(datestring, format)
    return datetime(*time_struct[0:6])


def convert_date_to_datetime(date):
    """Converts a datetime.date to a datetime.datetime object"""
    return datetime.combine(date, dtime()) if date else None


def date_before(date_cmp, years):
    today = datetime.now()
    then = datetime(today.year - years, today.month, today.day)
    return then > date_cmp


def date_after(*args, **kwargs):
    return not date_before(*args, **kwargs)


def find_day_of_week(year, month, day_of_week, offset=0, use_datetime=False):
    """
    Finds the day-of-week inside of a month
    year = an integer 4-digit year
    month = 1-12
    day_of_week = 0:monday, 6:sunday
    offset = week in the month, 0: first week, 1: second week, etc.
    """
    iter = Calendar().itermonthdates(year, month)
    n = 0

    for value in iter:
        if month != value.month:
            continue

        if day_of_week == weekday(value.year, value.month, value.day):
            if n == offset:
                return convert_date_to_datetime(value) if use_datetime else value
            else:
                n += 1

    return None


def is_recent(datetime_to_compare, *args_for_timedelta, **kwargs_for_timedelta):
    """
    Test if the dt is within the last minute or use the args and kwargs to build a timedelta.
    """
    now = datetime.now()

    if not args_for_timedelta:
        args_for_timedelta = []

    if not kwargs_for_timedelta:
        kwargs_for_timedelta = {'minutes': 1}

    return (now - timedelta(*args_for_timedelta, **kwargs_for_timedelta)) < datetime_to_compare


def time_in_millis(my_time=None):
    """
    Fetches the current time in milliseconds from epoch. By default it uses the UTC time, but you can pass in a any time. Must pass in a time tuple.
    """

    if my_time:
        t = my_time
    else:
        t = gmtime()

    return timegm(t)


def years_ago(some_date, years):
    """Return a date some number of calendar years before some given date.

    Leap years make subtracting multiples of 365 troublesome, so we just frob
    the calendar year and then, if the resulting date is on a nonexistent
    February 29, fall back to Feb 28.

    """
    try:
        new_date = date(some_date.year - years, some_date.month, some_date.day)
    except ValueError:
        new_date = date(some_date.year - years, 2, 28)
    return new_date


# ISO functions are from:
# http://stackoverflow.com/questions/304256/whats-the-best-way-to-find-the-inverse-of-datetime-isocalendar
def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = date(iso_year, 1, 4)
    delta = timedelta(fourth_jan.isoweekday() - 1)
    return fourth_jan - delta


def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + timedelta(days=iso_day - 1, weeks=iso_week - 1)

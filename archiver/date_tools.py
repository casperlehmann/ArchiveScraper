import datetime
import re

def get_date_as_string_YYYY_mm_dd(date):
    if not isinstance (date, datetime.datetime):
        raise TypeError
    return '{}-{}-{}'.format(
        date.year,
        str(date.month).zfill(2),
        str(date.day).zfill(2))

def get_date_as_string_YYYYmmdd(date):
    if not isinstance (date, datetime.datetime):
        raise TypeError
    return '{}{}{}'.format(
        date.year,
        str(date.month).zfill(2),
        str(date.day).zfill(2))

def get_date_string_generator(
        from_date = 'today',
        earliest_date = '2010-01-01',
        date_formatter = get_date_as_string_YYYYmmdd):
    earliest_date = get_date(earliest_date)
    earliest_date = date_formatter(earliest_date)
    from_date = get_date(from_date)
    i = 0
    while True:
        date = from_date - datetime.timedelta(days=i)
        date_string = date_formatter(date)
        yield date_string
        i += 1
        if earliest_date == date_string:
            break

def get_date(date_string):
    if not isinstance (date_string, str):
        raise TypeError
    if not (date_string == 'today' or
            re.match(r'\d\d\d\d-\d\d-\d\d', date_string)):
        raise ValueError
    if date_string == 'today': date_string = datetime.datetime.today()
    else: date_string = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    return date_string

import re

from archiver.date_tools import get_date, get_date_string_generator

def get_archive_urls(
        from_date='today', earliest_date='2012-02-06', schema='{}'):
    """ Create a list of urls from dates [from_date:earliest_date].
    """
    if not isinstance (from_date, str):
        raise TypeError
    if not (from_date == 'today' or
            re.match(r'\d\d\d\d-\d\d-\d\d', from_date)):
        raise ValueError
    if not isinstance (earliest_date, str):
        raise TypeError
    if not re.match(r'\d\d\d\d-\d\d-\d\d', earliest_date):
        raise ValueError
    if not isinstance (schema, str):
        raise TypeError
    if not '{}' in schema:
        raise ValueError('Cannot use str.format on supplied schema. Needs {}')

    get_date(from_date)
    out = []
    for date in get_date_string_generator(
            from_date=from_date,
            earliest_date=earliest_date):
        out.append(schema.format(date))
    return out


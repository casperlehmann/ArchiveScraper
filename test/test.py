from nose.tools import assert_equals, assert_not_equals
from nose.tools import assert_is_instance
from nose.tools import assert_raises, raises

import datetime

from archiver import archiver

class TestGetArchiveUrls(object):

    @classmethod
    def setup_class(cls):
        cls.data = archiver.get_archive_urls(from_date = '2016-04-01')

    @classmethod
    def teardown_class(cls):
        pass

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_type_urls(self):
        assert_is_instance(
            self.data,
            (list,))

    def test_len_urls(self):
        assert_equals(
            len(self.data),
            1517)

    def test_type_url(self):
        assert_is_instance(
            self.data[0],
            (str,))

    def test_first_url(self):
        assert_equals(
            self.data[0],
            'http://politics.people.com.cn/GB/70731/review/20160401.html')

    def test_final_url(self):
        assert_equals(
            self.data[-1],
            'http://politics.people.com.cn/GB/70731/review/20120206.html')

    def test_from_date_not_string(self):
        assert_raises(
            TypeError,
            archiver.get_archive_urls,
            20160401)

    def test_from_date_string_wrong_format(self):
        assert_raises(
            ValueError,
            archiver.get_archive_urls,
            '2016-4-1')

class TestGetDateStringeGenerator(object):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup(self):
        self.dates = archiver.get_date_string_generator(
            from_date = '2015-04-01',
            earliest_date='2015-01-01',
            date_formatter=archiver.get_date_as_string_YYYYmmdd)

    def teardown(self):
        pass

    def test_first_date(self):
        for generator_item, number in zip(self.dates, ['20150401']):
            assert_equals(generator_item, number)

    def test_len(self):
        assert_equals(len(list(self.dates)), 91)

    def test_first_date_YYYY_mm_dd(self):
        dates = archiver.get_date_string_generator(
            from_date = '2015-04-01',
            earliest_date='2015-01-01',
            date_formatter=archiver.get_date_as_string_YYYY_mm_dd)
        for generator_item, number in zip(dates, ['2015-04-01']):
            assert_equals(generator_item, number)

class TestGetDateAsString(object):

    def test_input_not_date_time(self):
        assert_raises(
            TypeError,
            archiver.get_date_as_string_YYYY_mm_dd,
            '2015-09-01')

    def test_input_date_time(self):
        date_string = '2015-09-01'
        assert_equals(
            archiver.get_date_as_string_YYYY_mm_dd(
                datetime.datetime.strptime(date_string, '%Y-%m-%d')),
            date_string)

    def test_input_not_date_time(self):
        assert_raises(
            TypeError,
            archiver.get_date_as_string_YYYYmmdd,
            '2015-09-01')

    def test_input_date_time(self):
        date_string = '20150901'
        assert_equals(
            archiver.get_date_as_string_YYYYmmdd(
                datetime.datetime.strptime(date_string, '%Y%m%d')),
            date_string)

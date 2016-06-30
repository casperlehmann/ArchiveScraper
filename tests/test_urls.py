""" Test getting urls for archive.

"""

from nose.tools import assert_equals

# pylint: disable=missing-docstring,no-self-use,attribute-defined-outside-init,too-many-public-methods,protected-access

from nose.tools import assert_is_instance
from nose.tools import assert_raises

import archiver

class TestGetArchiveUrls(object):

    @classmethod
    def setup_class(cls):
        """Generate urls for the politics.people.com.cn archive (2012-2016).
        """
        cls.data = archiver.get_archive_urls(
            from_date = '2016-04-01',
            earliest_date='2012-02-06',
            schema = 'http://politics.people.com.cn/GB/70731/review/{}.html')

    def test_type_urls(self):
        assert_is_instance(self.data, (list,))

    def test_len_urls(self):
        assert_equals(len(self.data), 1517)

    def test_type_url(self):
        assert_is_instance(self.data[0], (str,))

    def test_first_url(self):
        assert_equals(
            self.data[0],
            'http://politics.people.com.cn/GB/70731/review/20160401.html')

    def test_final_url(self):
        assert_equals(
            self.data[-1],
            'http://politics.people.com.cn/GB/70731/review/20120206.html')

    def test_from_date_raises_TypeError(self):
        assert_raises(TypeError, archiver.get_archive_urls, 20160401)

    def test_from_date_raises_ValueError(self):
        assert_raises(ValueError, archiver.get_archive_urls, '2016-4-1')

    def test_earliest_date_raises_TypeError(self):
        assert_raises(
            TypeError, archiver.get_archive_urls, earliest_date=20160401)

    def test_earliest_date_raises_ValueError(self):
        assert_raises(
            ValueError, archiver.get_archive_urls, earliest_date='20160401')

    def test_earliest_date_string_raises_ValueError(self):
        assert_raises(ValueError, archiver.get_archive_urls, '2016-4-1')

    def test_schema_raises_TypeError(self):
        assert_raises(TypeError, archiver.get_archive_urls, schema = 1)

    def test_schema_raises_ValueError(self):
        assert_raises(
            ValueError, archiver.get_archive_urls, from_date='today',
            earliest_date='2012-02-06', schema = '[]')

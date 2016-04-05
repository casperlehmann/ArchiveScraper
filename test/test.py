from nose.tools import assert_equals, assert_not_equals
from nose.tools import assert_is_instance
from nose.tools import assert_raises, raises

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

    def test_from_date_string_wrong_len(self):
        assert_raises(
            ValueError,
            archiver.get_archive_urls,
            '2016-4-1')

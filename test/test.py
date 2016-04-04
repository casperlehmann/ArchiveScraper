import nose
from nose.tools import assert_equals, assert_not_equals
from nose.tools import assert_raises, raises
#print (dir (nose.tools))

class TestCase(object):

    @classmethod
    def setup_class(cls):
        print ('##')

    @classmethod
    def teardown_class(cls):
        print ('##')

    def setup(self):
        print ('#')

    def teardown(self):
        print ('#')

    def test_this(self):
        print ('Test')

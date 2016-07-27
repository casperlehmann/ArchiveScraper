""" Test suite

"""

import tempfile
import os
import shutil

from glob import glob

from nose.tools import assert_equals#, assert_not_equals
from nose.tools import assert_raises
from nose.tools import assert_true, assert_false
from nose.plugins.skip import SkipTest

import archiver

# pylint: disable=missing-docstring,no-self-use,attribute-defined-outside-init,too-many-public-methods,protected-access

class TestAgent(object):

    skip_online_tests = True

    @classmethod
    def setup_class(cls):
        cls.temp_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(cls.temp_dir, 'archives'))

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.temp_dir)

    def setup(self):
        self.agent = archiver.Agent(
            directory = self.temp_dir, archive_folder = 'archives', db = 'db')

    def teardown(self):
        self.agent.clean()

    # __init__
    def test_directory_raises_TypeError(self):
        assert_raises(TypeError, archiver.Agent, directory = 1)

    def test_directory_raises_ValueError(self):
        assert_raises(
            ValueError, archiver.Agent, directory = '',
            archive_folder = 'archives', db = 'db')

    def test_isdir_temp(self):
        assert_true(os.path.isdir(self.temp_dir))

    # Archive
    def test__save_filename(self):
        row_id = self.agent.db.set_filename('www.example.com')
        retrieved = self.agent.db.get_filename('www.example.com')
        assert_equals(row_id, '000001')
        assert_equals(retrieved, '000001')

    def test__save_filename_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent.db.set_filename,
            url = 1, fname = '000001')

    def test__save_filename_fname_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent.db.set_filename,
            url = 'www.example.com', fname = 1)

    # Cleaning
    def test_clean(self):
        self.agent.fh.archive_folder = 'archives'
        archive = self.agent.fh.archive_folder
        fpath = os.path.join(archive, '000001')
        with open(fpath, 'wb') as f: f.write(b'Some contents')
        archive_folder = os.path.join(self.temp_dir, 'archives')

        # One file, one dir, one data, archive_folder, fpath:
        assert_true(os.path.isdir(archive_folder))
        assert_true(os.path.isfile(fpath))
        # ./archive/ ./archive.json ./scanned.json
        assert_equals(2, len(glob(os.path.join(self.agent.fh.directory,'*'))))
        assert_equals(1, len(glob(os.path.join(self.agent.fh.archive_folder,'*'))))

        # Delete it:
        self.agent.clean()
        # Files and dir are gone:
        assert_false(os.path.isdir(archive_folder))
        assert_false(os.path.isfile(fpath))
        # Root directory is empty:
        assert_equals(0, len(glob(os.path.join(self.agent.fh.directory,'*'))))
        # Recreate, so teardown doesn't fail:
        self.agent = archiver.Agent(
            directory = self.temp_dir, archive_folder = 'archives', db = 'db')

        assert_equals(2, len(glob(os.path.join(self.agent.fh.directory,'*'))))

        # Delete it:
        self.agent.clean()

        # Root directory is empty:
        assert_equals(0, len(glob(os.path.join(self.agent.fh.directory,'*'))))

        # Recreate, so teardown doesn't fail:
        self.agent = archiver.Agent(
            directory = self.temp_dir, archive_folder = 'archives', db = 'db')

    # File names and paths
    def test__get_filename_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent.db.get_filename, url=['not a string'])

    def test__get_filename_url_raises_KeyError(self):
        assert_raises(
            KeyError, self.agent.db.get_filename, url='www.example.com')

    def test__get_filename(self):
        self.agent.fh.archive_folder = 'archives'
        archive = self.agent.fh.archive_folder
        fname = self.agent.db.set_filename('www.example.com')
        fpath = os.path.join(archive, fname)
        with open(fpath, 'wb') as f: f.write(b'Some contents')
        assert_equals(self.agent.db.get_filename('www.example.com'), '000001')

    def test__get_filepath_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent.db.get_filepath, url = ['not a string'])

    def test__get_filepath_url_raises_KeyError(self):
        assert_raises(
            KeyError, self.agent.db.get_filepath, url='www.example.com')

    def test__get_filepath_file_raises_OSError(self):
        self.agent.db.set_filename('www.example.com')
        assert_raises(
            OSError, self.agent.db.get_filepath, url='www.example.com')

    def test__get_filepath(self):
        self.agent.fh.archive_folder = 'archives'
        archive = self.agent.fh.archive_folder
        fname = self.agent.db.set_filename('www.example.com')
        fpath = os.path.join(archive, fname)
        with open(fpath, 'wb') as f: f.write(b'Some contents')
        assert_equals(self.agent.db.get_filepath('www.example.com'), fpath)

    def test__get_archive_folder_sets_folder_name(self):
        assert_equals(str(self.agent.fh.archive_folder)[-9:], '/archives')
        self.agent.fh.archive_folder = 'test'
        assert_equals(
            self.agent.fh.archive_folder,
            os.path.join(self.temp_dir, 'test'))

    def test__get_archive_folder_archive_folder_raises_TypeError(self):
        def name_setter(name):
            self.agent.fh.archive_folder = name
        assert_raises(
            TypeError,
            name_setter,
            1)

    def test__get_archive_folder_creates_dirs(self):
        test_dir = os.path.join(self.temp_dir, 'test_dir')
        assert_false(os.path.exists(test_dir))
        self.agent.fh.archive_folder = test_dir
        assert_true(os.path.exists(test_dir))

    def test__get_archive_folder_stays_the_same(self):
        test_dir = os.path.join(self.temp_dir, 'test_dir')
        self.agent.fh.archive_folder = test_dir
        a = self.agent.fh.archive_folder
        self.agent.fh.archive_folder = test_dir
        b = self.agent.fh.archive_folder
        assert_equals(a,b)

    # Data
    def test__load_pages_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent.scraper.load_page, url = 1)

    def test__load_pages_raises_KeyError_when_page_not_saved(self):
        if self.skip_online_tests: raise SkipTest
        assert_raises(
            KeyError, self.agent.scraper.load_page, url = 'www.example.com')

    def test__load_pages(self):
        self.agent.fh.archive_folder = 'archives'
        fname = self.agent.db.set_filename('www.example.com')
        retrieved = self.agent.scraper.load_page(
            url = 'www.example.com')
        assert_equals(fname, '000001')
        assert_equals(retrieved, '000001')

    def test__fetch_page_url_raises_TypeError(self):
        if self.skip_online_tests: raise SkipTest
        assert_raises(
            TypeError, self.agent.scraper._fetch_page, url = 1)

    def test__fetch_page_writes_file(self):
        if self.skip_online_tests: raise SkipTest
        self.agent.scraper._fetch_page(url = 'www.example.com')
        self.agent.fh.archive_folder = 'archive_folder'
        expected_name = '000001'
        assert_equals(self.agent.db.get_filename, expected_name)

    def test__fetch_article_page(self):
        pass

    # Scanned
    def test__save_links_from_page(self):
        self.agent.analyzer._save_links_from_page('www.example.com', ['link_1'])
        assert_equals(self.agent.db.get_all_links(), [('link_1',)])
        self.agent.analyzer._save_links_from_page('www.example2.com', ['link_2'])
        assert_equals(self.agent.db.get_all_links(), [('link_1',), ('link_2',)])

    def test__save_scanned_url_raises_TypeError(self):
        assert_raises(TypeError, self.agent.analyzer._save_links_from_page, url = 1)

    def test__save_scanned_self_scanned_raises_TypeError(self):
        self.agent.file_name_data = ''
        assert_raises(TypeError, self.agent.analyzer._save_links_from_page, url = 'a')

    def test__save_archive_links(self):
        self.agent.analyzer._save_links_from_page('www.example.com', ['www.link.com'])
        assert_equals(self.agent.db.get_all_links(), [('www.link.com',)])

    def test__save_archive_links_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent.analyzer._save_links_from_page,
            url = 1, links = None)

    def test__save_archive_links_fname_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent.analyzer._save_links_from_page,
            url = 'www.example.com', links = None)

    def test_get_soup_file_raises_OSError(self):
        assert_raises(
            KeyError, self.agent.analyzer.get_soup, url = '000001')

    def test_get_soup(self):
        url = 'wikipedia.org'
        self.agent.fh.archive_folder = 'archives'
        archive = self.agent.fh.archive_folder
        fname = self.agent.db.set_filename(url)
        fpath = os.path.join(archive, fname)
        with open(fpath, 'wb') as f: f.write(b'Some contents')

        soup = self.agent.analyzer.get_soup(url)
        assert_equals(soup.text, 'Some contents')

    def test_get_soup_filename_raises_TypeError(self):
        assert_raises(TypeError, self.agent.analyzer.get_soup, fname=1, url='string')

    def test_get_soup_url_raises_TypeError(self):
        string = '000001'
        not_string = 1
        assert_raises(
            TypeError, self.agent.analyzer.get_soup, fname=string, url=not_string)

    def test_get_soup_raises_OSError(self):
        string = '000001'
        assert_raises(KeyError, self.agent.analyzer.get_soup, url=string)

    #def test_find_links_in_page_loads_from_disk(self):
    #    fname = '000001'
    #    archive = os.path.join(self.temp_dir, 'archives')
    #    os.makedirs(archive, exist_ok=True)
    #    fpath = os.path.join(archive, fname)
    #    html_contents = (b'<html><head></head><body>'
    #                     b'<a href="www.link.com">string</a>'
    #                     b'</body></html>')
    #    with open(fpath, 'wb') as f: f.write(html_contents)
    #    url = 'www.example.com'
    #    archive_data = {url: {'f': fname, 'l': ['www.link.com']}}
    #    archive_scanned_json_file = os.path.join(self.temp_dir, 'archive.json')
    #    with open(archive_scanned_json_file, 'w') as f:
    #        json.dump(archive_data, f)
    #    self.agent.file_name_data[url]['f'] = fname

    #    self.agent.find_links_in_page(url)
    #    assert_equals(
    #        archive_data,
    #        {'www.example.com': {'f': '000001', 'l': ['www.link.com']}})

    def test_find_links_in_page_raises_KeyError(self):
        assert_raises(
            KeyError, self.agent.analyzer.find_links_in_page, url = 'www.example.com')

    def test_find_links_in_page_url_raises_TypeError(self):
        assert_raises(TypeError, self.agent.analyzer.find_links_in_page, 1)

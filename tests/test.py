""" Test suite

"""

import tempfile
import os
import json
import shutil

from glob import glob

from nose.tools import assert_equals#, assert_not_equals
from nose.tools import assert_is_instance, assert_is_none
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
            naming_json_file = 'archive.json', scanned_json_file = 'scanned.json',
            directory = self.temp_dir, archive_folder = 'archives', db = 'db')

    def teardown(self):
        self.agent.clean()

    # __init__
    def test_directory_raises_TypeError(self):
        assert_raises(
            TypeError, archiver.Agent, directory = 1,
            naming_json_file = 'archive.json',
            scanned_json_file = 'scanned.json')

    def test_directory_raises_ValueError(self):
        assert_raises(
            ValueError, archiver.Agent, directory = '',
            naming_json_file = '1_archives.json', scanned_json_file = '1_scanned.json',
            archive_folder = '1_archives', db = 'db')

    def test_naming_json_file_sets_json(self):
        self.agent.clean()
        self.agent.file_name_data = None
        self.agent = archiver.Agent(
            naming_json_file = 'archive.json', scanned_json_file = 'scanned.json',
            directory = self.temp_dir, archive_folder = 'archives', db = 'db')
        assert_equals(self.agent.file_name_data, {})

    def test_isdir_temp(self):
        assert_true(os.path.isdir(self.temp_dir))

    def test_isfile_json_file(self):
        assert_true(os.path.isfile(self.agent.naming_json_file))

    # Archive
    def test_load_file_names_data_files_reads_contents_from_file(self):
        with open(os.path.join(self.temp_dir, 'archive.json'), 'w') as f:
            json.dump(
                {'www.example.com': {'f': '000001', 'l': ['www.link.com']}},
                f)
        assert_equals(self.agent.file_name_data, {})

        self.agent.naming_json_file = 'archive.json'
        assert_equals(
            self.agent.file_name_data,
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}})

        with open(os.path.join(self.temp_dir, 'scanned.json'), 'w') as f:
            json.dump(
                {'url_1': 'link_1', 'url_2': 'link_2', 'url_3': 'link_3'},
                f)
        self.agent.file_name_data = {}
        assert_equals(self.agent.file_name_data, {})

        self.agent.scanned_json_file = 'scanned.json'
        assert_equals(
            self.agent.scanned_file_data,
            {'url_1': 'link_1', 'url_2': 'link_2', 'url_3': 'link_3'})

    def test_load_file_names_data_files_creation(self):
        self.agent.file_name_data = None
        assert_is_none(self.agent.file_name_data)
        self.agent.naming_json_file = 'archive.json'
        assert_is_instance(self.agent.file_name_data, dict)
        assert_equals(self.agent.file_name_data, {})

    def test_load_file_names_data_files_load_file(self):
        with open(os.path.join(self.temp_dir, 'archive.json'), 'w') as f:
            f.write(json.dumps(
                {'www.example.com': {'f': '000001', 'l': ['www.link.com']}}))

        self.agent.file_name_data = None
        assert_is_none(self.agent.file_name_data)

        self.agent.naming_json_file = 'archive.json'
        assert_is_instance(self.agent.file_name_data, dict)
        assert_equals(
            self.agent.file_name_data,
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}})

        with open(os.path.join(self.temp_dir, 'scanned.json'), 'w') as f:
            json.dump(
                {'url_1': 'link_1', 'url_2': 'link_2', 'url_3': 'link_3'},
                f)

        self.agent.file_name_data = None
        assert_is_none(self.agent.file_name_data)

        self.agent.scanned_json_file = 'scanned.json'
        assert_is_instance(self.agent.scanned_file_data, dict)
        assert_equals(
            self.agent.scanned_file_data,
            {'url_1': 'link_1', 'url_2': 'link_2', 'url_3': 'link_3'})


    def test__save_filename(self):
        self.agent._save_filename('www.example.com', '000001')
        assert_equals(
            json.load(open(self.agent.naming_json_file)),
            {'www.example.com': {'f': '000001'}})

    def test__save_filename_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent._save_filename,
            url = 1, fname = '000001')

    def test__save_filename_fname_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent._save_filename,
            url = 'www.example.com', fname = 1)

    # Cleaning
    def test_clean(self):
        self.agent.archive_folder = 'archives'
        archive = self.agent.archive_folder
        fpath = os.path.join(archive, '000001')
        with open(fpath, 'wb') as f: f.write(b'Some contents')
        archive_json_file = os.path.join(self.temp_dir, 'archive.json')
        archive_folder = os.path.join(self.temp_dir, 'archives')

        # One file, one dir, one data, archive_json_file, archive_folder, fpath:
        assert_true(os.path.isfile(archive_json_file))
        assert_true(os.path.isdir(archive_folder))
        assert_true(os.path.isfile(fpath))
        # ./archive/ ./archive.json ./scanned.json
        assert_equals(4, len(glob(os.path.join(self.agent.directory,'*'))))
        assert_equals(2, len(glob(os.path.join(self.agent.archive_folder,'*'))))

        # Delete it:
        self.agent.clean()
        # Files and dir are gone:
        assert_false(os.path.isfile(archive_json_file))
        assert_false(os.path.isdir(archive_folder))
        assert_false(os.path.isfile(fpath))
        # Root directory is empty:
        assert_equals(0, len(glob(os.path.join(self.agent.directory,'*'))))
        # Recreate, so teardown doesn't fail:
        self.agent = archiver.Agent(
            naming_json_file = 'archive.json', scanned_json_file = 'scanned.json',
            directory = self.temp_dir, archive_folder = 'archives', db = 'db')

        # Scanned
        scanned_scanned_json_file = os.path.join(self.temp_dir, 'scanned.json')
        assert_true(os.path.isfile(scanned_scanned_json_file))

        # Only one file scanned_scanned_json_file:
        assert_true(os.path.isfile(scanned_scanned_json_file))
        assert_equals(4, len(glob(os.path.join(self.agent.directory,'*'))))

        # Delete it:
        self.agent.clean()

        # Files and dir are gone:
        assert_false(os.path.isfile(scanned_scanned_json_file))
        # Root directory is empty:
        assert_equals(0, len(glob(os.path.join(self.agent.directory,'*'))))

        # Recreate, so teardown doesn't fail:
        self.agent = archiver.Agent(
            naming_json_file = 'archive.json', scanned_json_file = 'scanned.json',
            directory = self.temp_dir, archive_folder = 'archives', db = 'db')

    # File names and paths
    def test__get_filename_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent._get_filename, url=['not a string'])

    def test__get_filename_url_raises_KeyError(self):
        assert_raises(
            KeyError, self.agent._get_filename, url='www.example.com')

    def test__get_filename(self):
        fname = '000001'
        self.agent.archive_folder = 'archives'
        archive = self.agent.archive_folder
        fpath = os.path.join(archive, fname)
        with open(fpath, 'wb') as f: f.write(b'Some contents')
        self.agent._save_filename('www.example.com', fname)
        assert_equals(self.agent._get_filename('www.example.com'), '000001')

    def test__get_filepath_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent._get_filepath, url = ['not a string'])

    def test__get_filepath_url_raises_KeyError(self):
        assert_raises(
            KeyError, self.agent._get_filepath, url='www.example.com')

    def test__get_filepath_file_raises_OSError(self):
        self.agent._save_filename('www.example.com', '000001')
        assert_raises(
            OSError, self.agent._get_filepath, url='www.example.com')

    def test__get_filepath(self):
        fname = '000001'
        self.agent.archive_folder = 'archives'
        archive = self.agent.archive_folder
        fpath = os.path.join(archive, fname)
        with open(fpath, 'wb') as f: f.write(b'Some contents')
        self.agent._save_filename('www.example.com', fname)
        assert_equals(self.agent._get_filepath('www.example.com'), fpath)

    def test__get_archive_folder_sets_folder_name(self):
        assert_equals(self.agent._archive_folder[-9:], '/archives')
        self.agent.archive_folder = 'test'
        assert_equals(
            self.agent._archive_folder,
            os.path.join(self.temp_dir, 'test'))

    def test__get_archive_folder_archive_folder_raises_TypeError(self):
        def name_setter(name):
            self.agent.archive_folder = name
        assert_raises(
            TypeError,
            name_setter,
            1)

    def test__get_archive_folder_creates_dirs(self):
        test_dir = os.path.join(self.temp_dir, 'test_dir')
        assert_false(os.path.exists(test_dir))
        self.agent.archive_folder = test_dir
        assert_true(os.path.exists(test_dir))

    def test__get_archive_folder_stays_the_same(self):
        test_dir = os.path.join(self.temp_dir, 'test_dir')
        self.agent.archive_folder = test_dir
        a = self.agent._archive_folder
        self.agent.archive_folder = test_dir
        b = self.agent._archive_folder
        assert_equals(a,b)

    # Data
    def test__load_archive_pages_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent.load_archive_page, url = 1)

    def test__load_archive_pages_raises_KeyError_when_page_not_saved(self):
        if self.skip_online_tests: raise SkipTest
        assert_raises(
            KeyError, self.agent.load_archive_page, url = 'www.example.com')
        self.agent._save_filename('www.example.com', '000001')
        self.agent.load_archive_page(url = 'www.example.com')

    def test__load_archive_pages(self):
        fname = '000001'
        self.agent.archive_folder = 'archives'
        self.agent._save_filename('www.example.com', '000001')
        fname = self.agent.load_archive_page(
            url = 'www.example.com')
        assert_equals('000001', fname)

    def test__fetch_archive_page_url_raises_TypeError(self):
        if self.skip_online_tests: raise SkipTest
        assert_raises(
            TypeError, self.agent._fetch_archive_page, url = 1)

    def test__fetch_archive_page_writes_file(self):
        if self.skip_online_tests: raise SkipTest
        assert_equals(self.agent.file_name_data, {})
        self.agent._fetch_archive_page(url = 'www.example.com')
        self.agent.archive_folder = 'archive_folder'
        expected_name = '000000'
        expected_archive_data = {'http://www.example.com': {'f': expected_name}}
        assert_equals(self.agent.file_name_data, expected_archive_data)

    def test__fetch_article_page(self):
        pass

    #class TestArticleScanner(object):
    def test_isfile_scanned_json_file(self):
        assert_true(os.path.isfile(self.agent.scanned_json_file))

    # Scanned
    def test__save_links_from_page(self):
        self.agent._save_links_from_page('www.example.com', ['link_1'])
        assert_equals(
            json.load(open(self.agent.scanned_json_file)),
            {'www.example.com': ['link_1']})
        self.agent._save_links_from_page('www.example2.com', ['link_2'])
        assert_equals(
            json.load(open(self.agent.scanned_json_file)),
            {'www.example.com': ['link_1'], 'www.example2.com': ['link_2']})

    def test__save_scanned_url_raises_TypeError(self):
        assert_raises(TypeError, self.agent._save_links_from_page, url = 1)

    def test__save_scanned_self_scanned_raises_TypeError(self):
        self.agent.file_name_data = ''
        assert_raises(TypeError, self.agent._save_links_from_page, url = 'a')

    def test__save_archive_links(self):
        self.agent._save_links_from_page('www.example.com', ['www.link.com'])
        assert_equals(
            json.load(open(self.agent.scanned_json_file)),
            {'www.example.com': ['www.link.com']})

    def test__save_archive_links_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent._save_links_from_page,
            url = 1, links = None)

    def test__save_archive_links_fname_raises_TypeError(self):
        assert_raises(
            TypeError, self.agent._save_links_from_page,
            url = 'www.example.com', links = None)

    def test_get_soup_file_raises_OSError(self):
        assert_raises(
            OSError, self.agent.get_soup, fname = '000001')

    def test_get_soup(self):
        fname = '000001'
        self.agent.archive_folder = 'archives'
        archive = self.agent.archive_folder
        fpath = os.path.join(archive, fname)
        with open(fpath, 'wb') as f: f.write(b'Some contents')

        soup = self.agent.get_soup(fname)
        assert_equals(soup.text, 'Some contents')

    def test_get_soup_filename_raises_TypeError(self):
        assert_raises(TypeError, self.agent.get_soup, fname=1, url='string')

    def test_get_soup_url_raises_TypeError(self):
        string = '000001'
        not_string = 1
        assert_raises(
            TypeError, self.agent.get_soup, fname=string, url=not_string)

    def test_get_soup_raises_OSError(self):
        string = '000001'
        assert_raises(OSError, self.agent.get_soup, fname=string, url=string)

    def test_find_links_in_page_loads_from_disk(self):
        fname = '000001'
        archive = os.path.join(self.temp_dir, 'archives')
        os.makedirs(archive, exist_ok=True)
        fpath = os.path.join(archive, fname)
        html_contents = (b'<html><head></head><body>'
                         b'<a href="www.link.com">string</a>'
                         b'</body></html>')
        with open(fpath, 'wb') as f: f.write(html_contents)
        url = 'www.example.com'
        archive_data = {url: {'f': fname, 'l': ['www.link.com']}}
        archive_scanned_json_file = os.path.join(self.temp_dir, 'archive.json')
        with open(archive_scanned_json_file, 'w') as f:
            json.dump(archive_data, f)
        self.agent.file_name_data[url]['f'] = fname

        self.agent.find_links_in_page(url)
        assert_equals(
            archive_data,
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}})

    def test_find_links_in_page_raises_KeyError(self):
        assert_raises(
            KeyError, self.agent.find_links_in_page, url = 'www.example.com')

    def test_find_links_in_page_url_raises_TypeError(self):
        assert_raises(TypeError, self.agent.find_links_in_page, 1)

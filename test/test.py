from nose.tools import assert_equals, assert_not_equals
from nose.tools import assert_is_instance, assert_is_none
from nose.tools import assert_raises, raises
from nose.tools import assert_true, assert_false
from nose.plugins.skip import SkipTest
import nose

import datetime
import tempfile
import os
import json
import shutil
from glob import glob

import archiver

class TestGetDateAsString(object):

    def test_date_YYYY_mm_dd_raises_TypeError(self):
        assert_raises(
            TypeError,
            archiver.get_date_as_string_YYYY_mm_dd,
            '2015-09-01')

    def test_date_YYYY_mm_dd(self):
        date_string = '2015-09-01'
        assert_equals(
            archiver.get_date_as_string_YYYY_mm_dd(
                datetime.datetime.strptime(date_string, '%Y-%m-%d')),
            date_string)

    def test_date_YYYYmmdd_raises_TypeError(self):
        assert_raises(
            TypeError,
            archiver.get_date_as_string_YYYYmmdd,
            '2015-09-01')

    def test_date_YYYYmmdd(self):
        date_string = '20150901'
        assert_equals(
            archiver.get_date_as_string_YYYYmmdd(
                datetime.datetime.strptime(date_string, '%Y%m%d')),
            date_string)

class TestGetDateStringeGenerator(object):

    def setup(self):
        self.dates = archiver.get_date_string_generator(
            from_date = '2015-04-01',
            earliest_date='2015-01-01',
            date_formatter=archiver.get_date_as_string_YYYYmmdd)

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

class TestGetDate(object):

    def test_date(self):
        assert_equals(
            archiver.get_date('2016-06-06'),
            datetime.datetime.strptime('20160606', '%Y%m%d'))

    def test_date_string_raises_TypeError(self):
        assert_raises(TypeError, archiver.get_date, 20160606)

    def test_date_string_raises_ValueError(self):
        assert_raises(ValueError, archiver.get_date, date_string='06=06-2016')

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

class TestDearchiver(object):

    skip_online_tests = True

    @classmethod
    def setup_class(cls):
        cls.temp_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(cls.temp_dir, 'archive'))

    @classmethod
    def teardown_class(cls):
        #cls.dearch._.close()
        shutil.rmtree(cls.temp_dir)

    def setup(self):
        self.dearch = archiver.Dearchiver(
            directory = self.temp_dir, silent = True)

    def teardown(self):
        self.dearch.clean(silent = True)

    # __init__
    def test_directory_raises_TypeError(self):
        assert_raises(
            TypeError, archiver.Dearchiver, directory = 1, silent = True)

    def test_directory_raises_ValueError(self):
        assert_raises(
            ValueError, archiver.Dearchiver, directory = '', silent = True)

    def test_load_data_files_sets_json(self):
        self.dearch.data = None
        self.dearch.load_data_files(silent = True)
        assert_equals(self.dearch.data, {})

    def test_isdir_temp(self):
        assert_true(os.path.isdir(self.temp_dir))

    def test_isfile_json_file(self):
        assert_true(os.path.isfile(self.dearch.json_file))

    # Archive
    def test_load_data_files_silent_raises_TypeError(self):
        assert_raises(TypeError, self.dearch.load_data_files, silent = 2)

    def test_load_data_files_reads_contents_from_file(self):
        json.dump(
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}},
            open(self.dearch.json_file, 'w'))
        assert_equals(self.dearch.data, {})

        self.dearch.load_data_files()
        assert_equals(
            self.dearch.data,
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}})

    def test_load_data_files_creation(self):
        self.dearch.data = None
        assert_is_none(self.dearch.data)
        self.dearch.load_data_files()
        assert_is_instance(self.dearch.data, dict)
        assert_equals(self.dearch.data, {})

    def test_load_data_files_load_file(self):
        with open(os.path.join(self.temp_dir, 'archive.json'), 'w') as f:
            f.write(json.dumps(
                {'www.example.com': {'f': '000001', 'l': ['www.link.com']}}))

        self.dearch.data = None
        assert_is_none(self.dearch.data)

        self.dearch.load_data_files()
        assert_is_instance(self.dearch.data, dict)
        assert_equals(
            self.dearch.data,
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}})

    def test__save_url(self):
        self.dearch._save_url('www.example.com', '000001')
        assert_equals(
            json.load(open(self.dearch.json_file)),
            {'www.example.com': {'f': '000001'}})

    def test__save_url_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.dearch._save_url,
            url = 1, fname = '000001')

    def test__save_url_fname_raises_TypeError(self):
        assert_raises(
            TypeError, self.dearch._save_url,
            url = 'www.example.com', fname = 1)

    # Cleaning
    def test_clean(self):
        archive = self.dearch._get_archive_folder(archive_folder = 'archive')
        fpath = os.path.join(archive, '000001.html')
        with open(fpath, 'wb') as f: f.write(b'Some contents')
        archive_json_file = os.path.join(self.temp_dir, 'archive.json')
        archive_folder = os.path.join(self.temp_dir, 'archive')

        # One file, one dir, one data, archive_json_file, archive_folder, fpath:
        assert_true(os.path.isfile(archive_json_file))
        assert_true(os.path.isdir(archive_folder))
        assert_true(os.path.isfile(fpath))
        assert_equals(2, len(glob(os.path.join(self.dearch.directory,'*'))))
        assert_equals(1, len(glob(os.path.join(self.dearch._archive_folder,'*'))))

        # Delete it:
        self.dearch.clean(silent = True)
        # Files and dir are gone:
        assert_false(os.path.isfile(archive_json_file))
        assert_false(os.path.isdir(archive_folder))
        assert_false(os.path.isfile(fpath))
        # Root directory is empty:
        assert_equals(0, len(glob(os.path.join(self.dearch.directory,'*'))))
        # Recreate, so teardown doesn't fail:
        self.dearch = archiver.Dearchiver(
            directory = self.temp_dir, silent = True)

    # File names and paths
    def test__get_filename_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.dearch._get_filename, url=['not a string'])

    def test__get_filename_url_raises_KeyError(self):
        assert_raises(
            KeyError, self.dearch._get_filename, url='www.example.com')

    def test__get_filename(self):
        fname = '000001'
        archive = self.dearch._get_archive_folder(
            archive_folder = 'archive')
        fpath = os.path.join(archive, fname)
        with open(fpath, 'wb') as f: f.write(b'Some contents')
        self.dearch._save_url('www.example.com', fname)
        assert_equals(self.dearch._get_filename('www.example.com'), '000001')

    def test__get_filepath_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.dearch._get_filepath, url = ['not a string'])

    def test__get_filepath_url_raises_KeyError(self):
        assert_raises(
            KeyError, self.dearch._get_filepath, url='www.example.com')

    def test__get_filepath_file_raises_OSError(self):
        self.dearch._save_url('www.example.com', '000001')
        assert_raises(
            OSError, self.dearch._get_filepath, url='www.example.com')

    def test__get_filepath(self):
        fname = '000001'
        archive = self.dearch._get_archive_folder(
            archive_folder = 'archive')
        fpath = os.path.join(archive, fname)
        with open(fpath, 'wb') as f: f.write(b'Some contents')
        self.dearch._save_url('www.example.com', fname)
        assert_equals(self.dearch._get_filepath('www.example.com'), fpath)

    def test__get_archive_folder_sets_folder_name(self):
        assert_is_none(self.dearch._archive_folder)
        self.dearch._get_archive_folder('test')
        assert_equals(
            self.dearch._archive_folder,
            os.path.join(self.temp_dir, 'test'))

    def test__get_archive_folder_returns_self_archive_folder(self):
        assert_equals(
            self.dearch._get_archive_folder(archive_folder = 'afn'),
            self.dearch._archive_folder)

    def test__get_archive_folder_default_archive_folder(self):
        self.dearch._archive_folder = None
        assert_equals(
            self.dearch._get_archive_folder(),
            os.path.join(self.temp_dir, 'archive'))

    def test__get_archive_folder_archive_folder_raises_TypeError(self):
        assert_raises(
            TypeError,
            self.dearch._get_archive_folder,
            archive_folder=1)

    def test__get_archive_folder_creates_dirs(self):
        test_dir = os.path.join(self.temp_dir, 'test_dir')
        assert_false(os.path.exists(test_dir))
        self.dearch._get_archive_folder(archive_folder=test_dir)
        assert_true(os.path.exists(test_dir))

    def test__get_archive_folder_stays_the_same(self):
        test_dir = os.path.join(self.temp_dir, 'test_dir')
        self.dearch._get_archive_folder(archive_folder=test_dir)
        a = self.dearch._archive_folder
        self.dearch._get_archive_folder(archive_folder=test_dir)
        b = self.dearch._archive_folder
        assert_equals(a,b)

    # Data
    def test__load_archive_pages_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.dearch.load_archive_page, url = 1, silent = True)

    def test__load_archive_pages_raises_KeyError_when_page_not_saved(self):
        if self.skip_online_tests: raise SkipTest
        assert_raises(
            KeyError, self.dearch.load_archive_page, url = 'www.example.com',
            silent = True)
        self.dearch._save_url('www.example.com', '000001')
        self.dearch.load_archive_page(url = 'www.example.com', silent = True)

    def test__load_archive_pages(self):
        fname = '000001'
        archive = self.dearch._get_archive_folder(
            archive_folder = 'archive')
        fpath = os.path.join(archive, fname)
        self.dearch._save_url('www.example.com', '000001')
        fname = self.dearch.load_archive_page(
            url = 'www.example.com', silent = True)
        assert_equals('000001', fname)

    def test__fetch_archive_page_url_raises_TypeError(self):
        if self.skip_online_tests: raise SkipTest
        assert_raises(
            TypeError, self.dearch._fetch_archive_page, url = 1, silent = True)

    def test__fetch_archive_page_writes_file(self):
        if self.skip_online_tests: raise SkipTest
        assert_equals(self.dearch.data, {})
        self.dearch._fetch_archive_page(url = 'www.example.com', silent = True)
        expected_path = os.path.join(self.dearch._archive_folder, '000000.html')
        expected_archive_data = {'http://www.example.com': {'f': expected_path}}
        assert_equals(self.dearch.data, expected_archive_data)

    def test__fetch_article_page(self):
        pass

class TestArticleGetter(object):

    skip_online_tests = True

    @classmethod
    def setup_class(cls):
        cls.temp_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(cls.temp_dir, 'archive'))

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.temp_dir)

    def setup(self):
        self.artget = archiver.ArticleGetter(
            directory = self.temp_dir, silent = True)

    def teardown(self):
        self.artget.clean(silent = True)

    def test_load_data_files_sets_json(self):
        self.artget.data = None
        self.artget.load_data_files(silent = True)
        assert_equals(self.artget.data, {})

    def test_isfile_json_file(self):
        assert_true(os.path.isfile(self.artget.json_file))

    # Articles
    def test_load_data_files_silent_raises_TypeError(self):
        assert_raises(TypeError, self.artget.load_data_files, silent = 2)

    def test_load_data_files_reads_contents_from_file(self):
        json.dump(
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}},
            open(self.artget.json_file, 'w'))
        assert_equals(self.artget.data, {})

        self.artget.load_data_files()
        assert_equals(
            self.artget.data,
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}})

    def test_load_data_files_creation(self):
        self.artget.data = None
        assert_is_none(self.artget.data)
        self.artget.load_data_files()
        assert_is_instance(self.artget.data, dict)
        assert_equals(self.artget.data, {})

    def test_load_data_files_load_file(self):
        with open(os.path.join(self.temp_dir, 'article.json'), 'w') as f:
            f.write(json.dumps(
                {'www.example.com': {'f': '000001', 'l': ['www.link.com']}}))

        self.artget.data = None
        assert_is_none(self.artget.data)

        self.artget.load_data_files()
        assert_is_instance(self.artget.data, dict)
        assert_equals(
            self.artget.data,
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}})

    def test__save_url(self):
        self.artget._save_url('www.example.com', '000001')
        assert_equals(
            json.load(open(self.artget.json_file)),
            {'www.example.com': {'f': '000001'}})

    def test__save_url_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.artget._save_url,
            url = 1, fname = '000001')

    def test__save_url_fname_raises_TypeError(self):
        assert_raises(
            TypeError, self.artget._save_url,
            url = 'www.example.com', fname = 1)

    def test__save_url_and_links(self):
        # We make sure that one doesn't overwrite the other:
        self.artget._save_url('www.example.com', '000001')
        self.artget._save_article_links('www.example.com', ['www.link.com'])
        # Manually load the dict from file and compare:
        assert_equals(
            json.load(open(self.artget.json_file)),
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}})

    def test__save_article_links(self):
        # Init file:
        self.artget._save_article_links('www.example.com', ['www.link.com'])
        # Manually load the dict from file and compare:
        assert_equals(
            json.load(open(self.artget.json_file)),
            {'www.example.com': {'l': ['www.link.com']}})

    def test__save_article_links_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.artget._save_article_links,
            url = 1, links = None)

    def test__save_article_links_fname_raises_TypeError(self):
        assert_raises(
            TypeError, self.artget._save_article_links,
            url = 'www.example.com', links = None)

    # Cleaning
    def test_clean(self):
        article_json_file = os.path.join(self.temp_dir, 'article.json')
        assert_true(os.path.isfile(article_json_file))

        # Only one file article_json_file:
        assert_true(os.path.isfile(article_json_file))
        assert_equals(1, len(glob(os.path.join(self.artget.directory,'*'))))

        # Delete it:
        self.artget.clean(silent = True)

        # Files and dir are gone:
        assert_false(os.path.isfile(article_json_file))
        # Root directory is empty:
        assert_equals(0, len(glob(os.path.join(self.artget.directory,'*'))))

        # Recreate, so teardown doesn't fail:
        self.artget = archiver.Dearchiver(
            directory = self.temp_dir, silent = True)

class TestArticleScanner(object):

    skip_online_tests = True

    @classmethod
    def setup_class(cls):
        cls.temp_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(cls.temp_dir, 'archive'))

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.temp_dir)

    def setup(self):
        self.artscan = archiver.ArticleScanner(
            directory = self.temp_dir, silent = True)

    def teardown(self):
        self.artscan.clean(silent = True)

    def test_load_data_files_sets_json(self):
        self.artscan.data = None
        self.artscan.load_data_files(silent = True)
        assert_equals(self.artscan.data, {})

    def test_isfile_json_file(self):
        assert_true(os.path.isfile(self.artscan.json_file))

    # Scanned
    def test_load_data_files_silent_raises_TypeError(self):
        assert_raises(TypeError, self.artscan.load_data_files, silent = 2)

    def test_load_data_files_reads_contents_from_file(self):
        with open(os.path.join(self.temp_dir, 'scanned.json'), 'w') as f:
            json.dump(
                {'url_1': 'link_1', 'url_2': 'link_2', 'url_3': 'link_3'},
                f)
        assert_equals(self.artscan.data, {})

        self.artscan.load_data_files()
        assert_equals(
            self.artscan.data,
            {'url_1': 'link_1', 'url_2': 'link_2', 'url_3': 'link_3'})

    def test_load_data_files_creation(self):
        self.artscan.data = None
        assert_is_none(self.artscan.data)
        self.artscan.load_data_files()
        assert_is_instance(self.artscan.data, dict)
        assert_equals(self.artscan.data, {})

    def test_load_data_files_load_file(self):
        with open(os.path.join(self.temp_dir, 'scanned.json'), 'w') as f:
            json.dump(
                {'url_1': 'link_1', 'url_2': 'link_2', 'url_3': 'link_3'},
                f)

        self.artscan.data = None
        assert_is_none(self.artscan.data)

        self.artscan.load_data_files()
        assert_is_instance(self.artscan.data, dict)
        assert_equals(
            self.artscan.data,
            {'url_1': 'link_1', 'url_2': 'link_2', 'url_3': 'link_3'})

    def test__save_scanned_links(self):
        self.artscan._save_scanned_links('www.example.com', ['link_1'])
        assert_equals(
            json.load(open(self.artscan.json_file)),
            {'www.example.com': ['link_1']})
        self.artscan._save_scanned_links('www.example2.com', ['link_2'])
        assert_equals(
            json.load(open(self.artscan.json_file)),
            {'www.example.com': ['link_1'], 'www.example2.com': ['link_2']})

    def test__save_scanned_url_raises_TypeError(self):
        assert_raises(TypeError, self.artscan._save_scanned_links, url = 1)

    def test__save_scanned_self_scanned_raises_TypeError(self):
        self.artscan.data = ''
        assert_raises(TypeError, self.artscan._save_scanned_links, url = 'a')

    def test__save_archive_links(self):
        # Init file:
        self.artscan._save_scanned_links('www.example.com', ['www.link.com'])
        # Manually load the dict from file and compare:
        assert_equals(
            json.load(open(self.artscan.json_file)),
            {'www.example.com': ['www.link.com']})

    def test__save_archive_links_url_raises_TypeError(self):
        assert_raises(
            TypeError, self.artscan._save_scanned_links,
            url = 1, links = None)

    def test__save_archive_links_fname_raises_TypeError(self):
        assert_raises(
            TypeError, self.artscan._save_scanned_links,
            url = 'www.example.com', links = None)

    # Cleaning
    def test_clean(self):
        scanned_json_file = os.path.join(self.temp_dir, 'scanned.json')
        assert_true(os.path.isfile(scanned_json_file))

        # Only one file scanned_json_file:
        assert_true(os.path.isfile(scanned_json_file))
        assert_equals(1, len(glob(os.path.join(self.artscan.directory,'*'))))

        # Delete it:
        self.artscan.clean(silent = True)

        # Files and dir are gone:
        assert_false(os.path.isfile(scanned_json_file))
        # Root directory is empty:
        assert_equals(0, len(glob(os.path.join(self.artscan.directory,'*'))))

        # Recreate, so teardown doesn't fail:
        self.artscan = archiver.Dearchiver(
            directory = self.temp_dir, silent = True)

    def test_get_soup_file_raises_OSError(self):
        assert_raises(
            OSError, self.artscan.get_soup, fname = '000001', silent = True)

    def test_get_soup(self):
        fname = '000001'
        archive = self.artscan._get_archive_folder(
            archive_folder = 'archive')
        fpath = os.path.join(archive, fname+'.html')
        with open(fpath, 'wb') as f: f.write(b'Some contents')

        soup = self.artscan.get_soup(fname, silent = True)
        assert_equals(soup.text, 'Some contents')

    def test_get_soup_filename_raises_TypeError(self):
        assert_raises(
            TypeError, self.artscan.get_soup, fname=1, url='string',
            silent = True)

    def test_get_soup_url_raises_TypeError(self):
        string = '000001'
        not_string = 1
        assert_raises(
            TypeError, self.artscan.get_soup, fname=string, url=not_string,
            silent = True)

    def test_get_soup_raises_OSError(self):
        string = '000001'
        assert_raises(
            OSError, self.artscan.get_soup, fname=string, url=string,
            silent = True)

    def test_find_links_in_page_loads_from_disk(self):
        fname = '000001'
        archive = os.path.join(self.temp_dir, 'archive')
        os.makedirs(archive, exist_ok=True)
        fpath = os.path.join(archive, fname + '.html')
        html_contents = (b'<html><head></head><body>'
                         b'<a href="www.link.com">string</a>'
                         b'</body></html>')
        with open(fpath, 'wb') as f: f.write(html_contents)
        url = 'www.example.com'
        archive_data = {url: {'f': fname, 'l': ['www.link.com']}}
        archive_json_file = os.path.join(self.temp_dir, 'archive.json')
        with open(archive_json_file, 'w') as f:
            json.dump(archive_data, f)
        self.artscan.data[url]['f'] = fname

        self.artscan.find_links_in_page(url, silent = True)
        assert_equals(
            archive_data,
            {'www.example.com': {'f': '000001', 'l': ['www.link.com']}})

    def test_find_links_in_page_raises_KeyError(self):
        assert_raises(
            KeyError, self.artscan.find_links_in_page, url = 'www.example.com')

    def test_find_links_in_page_url_raises_TypeError(self):
        assert_raises(TypeError, self.artscan.find_links_in_page, 1)


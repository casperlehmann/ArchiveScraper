import datetime
import json
import os
import re
import shutil
import urllib.request

from collections import defaultdict as dd
from bs4 import BeautifulSoup as bs
from glob import glob

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

class Dearchiver(object):
    """Starts from a list of archive urls and crawls links.
    """
    _directory = None
    archive_folder = None
    archive_meta = None
    article_data = None
    url_queue = []
    pages = []
    scanned = []
    links = {}

    def __init__(self, directory = None, silent = False):
        self.directory = directory
        self.archive_json_file = os.path.join(self.directory, 'archive.json')
        self.scanned_json_file = os.path.join(self.directory, 'scanned.json')
        self.article_json_file = os.path.join(self.directory, 'article.json')
        self.load_data_files(silent = silent)

    def load_data_files(self, silent = False):
        if not silent: print ('Loading data files...')
        self._load_archive_json(silent = silent)
        self._load_scanned_json(silent = silent)
        self._load_article_json(silent = silent)
        if not silent: print ()

    @property
    def directory(self):
        return self._directory

    @directory.setter
    def directory(self, directory):
        if directory is not None:
            if not isinstance (directory, str):
                raise TypeError('directory must be a string.')
            if not os.path.isdir(directory):
                raise ValueError('directory is not a directory.')
            self._directory = directory
        elif self._directory is None:
            self._directory = 'data_dearchiver'
        else:
            # self._directory already has a value
            pass

    # Archive
    def _load_archive_json(self, silent = False):
        if not isinstance(silent, bool):
            raise TypeError('Parameter \'silent\' must be of type bool')
        try:
            self.archive_meta = dd(
                lambda: dict(),
                json.load(open(self.archive_json_file)))
        except FileNotFoundError as e:
            if not silent: print ('Creating new file:', self.archive_json_file)
            self.archive_meta = dd(lambda: dict())
            json.dump(self.archive_meta, open(self.archive_json_file, 'w'))

    def _save_archive_url(self, url, fname):
        if not isinstance (url, str):
            raise TypeError
        if not isinstance (fname, str):
            raise TypeError
        self.archive_meta[url]['f'] = fname
        json.dump(self.archive_meta, open(self.archive_json_file, 'w'))

    def _save_archive_links(self, url, links):
        if not isinstance (url, str):
            raise TypeError
        if not isinstance (links, list):
            raise TypeError
        self.archive_meta[url]['l'] = links
        json.dump(self.archive_meta, open(self.archive_json_file, 'w'))

    # Articles
    def _load_article_json(self, silent = False):
        if not isinstance(silent, bool):
            raise TypeError('Parameter \'silent\' must be of type bool')
        try:
            self.article_data = dd(
                lambda: dict(),
                json.load(open(self.article_json_file)))
        except FileNotFoundError as e:
            if not silent: print ('Creating new file:', self.article_json_file)
            self.article_data = dd(lambda: dict())
            json.dump(self.article_data, open(self.article_json_file, 'w'))

    def _save_article_url(self, url, fname):
        if not isinstance (url, str):
            raise TypeError
        if not isinstance (fname, str):
            raise TypeError
        self.article_data[url]['f'] = fname
        json.dump(self.article_data, open(self.article_json_file, 'w'))

    def _save_article_links(self, url, links):
        if not isinstance (url, str):
            raise TypeError
        if not isinstance (links, list):
            raise TypeError
        self.article_data[url]['l'] = links
        json.dump(self.article_data, open(self.article_json_file, 'w'))

    # Scanned
    def _load_scanned_json(self, silent = False):
        if not isinstance(silent, bool):
            raise TypeError('Parameter \'silent\' must be of type bool')
        try:
            self.scanned = list(json.load(open(self.scanned_json_file)))
        except FileNotFoundError as e:
            if not silent: print ('Creating new file:', self.scanned_json_file)
            self.scanned = []
            json.dump(self.scanned, open(self.scanned_json_file, 'w'))

    def _save_scanned(self, url):
        if not isinstance (url, str):
            raise TypeError('url needs to be of type string.')
        if not isinstance (self.scanned, list):
            raise TypeError('self.scanned needs to be a list.')
        self.scanned.append(url)
        json.dump(self.scanned, open(self.scanned_json_file, 'w'))

    # Cleaning
    def clean(self, silent = False):
        if not silent: print ('Cleaning...')
        self.clean_json_archive(silent=silent)
        self.clean_json_article(silent=silent)
        self.clean_json_scanned(silent=silent)
        self.clean_archive(silent=silent)
        self.clean_project_root(silent=silent)
        self.archive_meta = None
        self.article_data = None
        self.scanned = None
        if not silent: print()

    def clean_json_archive(self, silent = False):
        try:
            if not silent: print ('Deleting: ' + self.archive_json_file + '...')
            os.remove(self.archive_json_file)
        except FileNotFoundError:
            if not silent: print ('Does not exist: ' + self.archive_json_file)

    def clean_json_article(self, silent = False):
        try:
            if not silent: print ('Deleting: ' + self.article_json_file + '...')
            os.remove(self.article_json_file)
        except FileNotFoundError:
            if not silent: print ('Does not exist: ' + self.article_json_file)

    def clean_json_scanned(self, silent = False):
        try:
            if not silent: print ('Deleting: ' + self.scanned_json_file + '...')
            os.remove(self.scanned_json_file)
        except FileNotFoundError:
            if not silent: print ('Does not exist: ' + self.scanned_json_file)

    def clean_archive(self, silent = False):
        for f in glob(os.path.join(self._get_archive_folder(), '*')):
            if not silent: print ('Deleting: ' + f)
            os.remove(f)

    def clean_project_root(self, silent = False):
        for f in glob(os.path.join(self.directory, '*')):
            if not silent: print ('Deleting: ' + f)
            shutil.rmtree(f)

    # File names and paths
    def _get_filename(self, url):
        if not isinstance (url, str):
            raise TypeError
        if not url in self.archive_meta:
            raise KeyError
        fname = self.archive_meta[url]['f']
        return fname

    def _get_filepath(self, url):
        if not isinstance (url, str):
            raise TypeError
        if not url in self.archive_meta:
            raise KeyError
        fname = self._get_filename(url)
        if not os.path.isfile(os.path.join(self._get_archive_folder(), fname)):
            raise OSError(('File {} does not exist.'.format(fname)))
        return os.path.join(self._get_archive_folder(), fname)

    def _get_archive_folder(self, archive_folder = None):
        if archive_folder is None:
            current = self.archive_folder
            if isinstance(current, str):
                archive_folder = current
            else:
                archive_folder = os.path.join(self.directory, 'archive')
        else:
            archive_folder = os.path.join(self.directory, archive_folder)
        if not isinstance(archive_folder, str):
            raise TypeError(
                'Name of archive folder must be a string, not {}'.format(
                    archive_folder))
        self.archive_folder = archive_folder
        os.makedirs(self.archive_folder, exist_ok=True)
        return self.archive_folder

    # Data
    def load_archive(self, archive, silent = False):
        for url in archive:
            self.load_archive_pages(url, silent = silent)

    def load_archive_pages(self, url, silent = False):
        if not isinstance (url, str):
            raise TypeError('url must be a string')
        try:
            fname = self._get_filename(url)
            if not silent: print ('Alredy here: {}'.format(url))
        except KeyError:
            if not silent: print ('Fetching...: {}'.format(url))
            self._fetch_archive_page(url, silent = silent)
            fname = self._get_filename(url)
        return fname

    def _fetch_archive_page(self, url, silent = False):
        if not isinstance(url, str):
            raise TypeError('url must be a string.')
        if not url.startswith('http'):
            url = 'http://' + url
        with urllib.request.urlopen(url) as url_obj:
            fname = os.path.join(
                self._get_archive_folder(),
                str(len(self.archive_meta)).zfill(6) + '.html')
            with open(fname, 'wb') as f:
                if not silent: print ('Writing file: {}'.format(fname))
                f.write(url_obj.read())
                self._save_archive_url(url, fname)

    def load_article_pages(self, *urls, silent = False):
        for url in urls:
            if url in self.article_data:
                self._get_filename(url)
                if not silent: print ('Alredy here')
            else:
                self._fetch_article_page(url, silent = silent)
                self._get_filename(url)

    def _fetch_article_page(self, url, silent = False):
        with urllib.request.urlopen(url) as url_obj:
            os.makedirs(os.path.join(self.directory, 'articles'), exist_ok=True)
            fname = os.path.join(
                self.directory, 'articles',
                str(len(self.article_data)).zfill(6) + '.html')
            with open(fname, 'wb') as f:
                if not silent: print ('Writing file: {}'.format(fname))
                f.write(url_obj.read())
                self._save_archive_url(url, fname)

    def get_soup(self, fname, url = 'not supplied', silent = False):
        if fname is None or not isinstance(fname, str):
            raise TypeError("fname must be a string.")
        if url is None or not isinstance(url, str):
            raise TypeError("url must be a string.")
        if not silent:
            print ('Loading & Souping file: [{}] for url: [{}]'.format(
                fname, url))
        try:
            fname = os.path.join(self._get_archive_folder(), fname)
            with open(fname, 'rb') as fobj:
                return bs(fobj.read(), 'html.parser')
        except FileNotFoundError:
            raise OSError

    def find_links_in_page(self, url, silent = False):
        if not isinstance(url, str):
            raise TypeError
        links = []
        try:
            fname = self._get_filename(url)
        except KeyError:
            raise FileNotFoundError(
                'File does not exist for url: {}'.format(url))
        for a in self.get_soup(fname, silent = silent).find_all('a'):
            if a.has_attr('href'):
                link = a.attrs['href'].strip()
                links.append(link)
        self._save_article_links(url, links)
        self._save_scanned(url)

    def find_links_in_archive(self, silent = False):
        for url in set(self.archive_meta.keys()):
            if not url in self.scanned:
                self.find_links_in_page(url, silent = silent)

    # Analysis
    def count_links(self, counter = None, links = None, domain = None):
        if links is None:
            links = [_ for key, item in self.archive_meta.items()
                     for _ in item['l']]
        if counter is None: counter = dd(int)
        if domain is None: domain = ''
        if domain == '': domain = 'politics.people.com.cn'
        for link in links:
            if domain in link:
                counter[link] += 1
        return counter

    def get_queue(self, filtr):
        queue = []
        for url, data in self.archive_meta.items():
            if url in self.scanned:
                queue.extend(data['l'])
        filtr = [_ for _ in queue if filtr in _]
        return filtr

    # Feedback
    def show_counter(self, counter, filtr = None, silent = False):
        if filtr is None:
            filtr = r'/[1-2][09][901][0-9]/'
        refiltered_count = {}
        for item in counter:
            if re.search(filtr, item) is not None:
                refiltered_count[item] = counter[item]
        for href, count in sorted(
                refiltered_count.items(),
                key=lambda x: x[0]):
            if not silent: print (href)

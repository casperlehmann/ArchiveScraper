import datetime
import json
import os
import re
import shutil
import urllib.request

from collections import defaultdict as dd
from bs4 import BeautifulSoup as bs
from glob import glob

from archiver.date_tools import get_date, get_date_string_generator

class ScraperBase(object):
    """Starts from a list of archive urls and crawls links.
    """
    _directory = None
    _archive_folder = None
    data = None

    def __init__(self, directory = None, silent = False):
        self.directory = directory
        self.load_json(silent = silent)
        self.load_data_files(silent = silent)

    def load_json(self, silent = False):
        raise NotImplementedError

    def load_data_files(self, silent = False):
        raise NotImplementedError

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

    # Cleaning
    def clean(self, silent = False):
        self.clean_project_root(silent=silent)

    def clean_json(self, target, silent = False):
        try:
            if not silent: print ('Deleting: ' + target + '...')
            os.remove(target)
        except FileNotFoundError:
            if not silent: print ('Does not exist: ' + target)

    def clean_project_root(self, silent = False):
        for f in glob(os.path.join(self.directory, '*')):
            if not silent: print ('Deleting: ' + f)
            shutil.rmtree(f)

    # File names and paths
    def _get_filename(self, url):
        if not isinstance (url, str):
            raise TypeError
        if not url in self.data:
            raise KeyError('File does not registered for url: {}'.format(url))
        fname = self.data[url]['f']
        return fname

    def _get_filepath(self, url):
        if not isinstance (url, str):
            raise TypeError
        if not url in self.data:
            raise KeyError
        fname = self._get_filename(url)
        if not os.path.isfile(os.path.join(self._get_archive_folder(), fname)):
            raise OSError(('File {} does not exist.'.format(fname)))
        return os.path.join(self._get_archive_folder(), fname)

    def _get_archive_folder(self, archive_folder = None):
        if archive_folder is None:
            current = self._archive_folder
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
        self._archive_folder = archive_folder
        os.makedirs(self._archive_folder, exist_ok=True)
        return self._archive_folder

    def _load_json(self, json_file, silent = False):
        if not isinstance(silent, bool):
            raise TypeError('Parameter \'silent\' must be of type bool')
        try:
            self.data = dd(lambda: dict(), json.load(open(json_file)))
        except FileNotFoundError as e:
            if not silent: print ('Creating new file:', json_file)
            self.data = dd(lambda: dict())
            json.dump(self.data, open(json_file, 'w'))

    # Data
    def load_archive(self, urls, silent = False):
        for url in urls:
            self.load_archive_page(url, silent = silent)

    def load_archive_page(self, url, silent = False):
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
            fname = str(len(self.data)).zfill(6)
            with open(fname, 'wb') as f:
                if not silent: print ('Writing file: {}'.format(fname))
                f.write(url_obj.read())
                self._save_archive_url(url, fname)

    def load_article_pages(self, *urls, silent = False):
        for url in urls:
            if url in self.data:
                self._get_filename(url)
                if not silent: print ('Alredy here')
            else:
                self._fetch_article_page(url, silent = silent)
                self._get_filename(url)

    def _fetch_article_page(self, url, silent = False):
        with urllib.request.urlopen(url) as url_obj:
            os.makedirs(os.path.join(self.directory, 'articles'), exist_ok=True)
            fname = str(len(self.data)).zfill(6)
            with open(fname, 'wb') as f:
                if not silent: print ('Writing file: {}'.format(fname))
                f.write(url_obj.read())
                self._save_archive_url(url, fname)

class Dearchiver(ScraperBase):
    archive_json_file = None

    def __init__(self, directory = None, silent = False):
        super().__init__(directory, silent)

    def load_json(self, silent = False):
        self.archive_json_file = os.path.join(self.directory, 'archive.json')

    def load_data_files(self, silent = False):
        if not silent: print ('Loading data files...')
        self._load_archive_json(silent = silent)
        if not silent: print ()

    # Archive
    def _load_archive_json(self, silent = False):
        super()._load_json(json_file = self.archive_json_file, silent = silent)

    def _save_archive_url(self, url, fname):
        if not isinstance (url, str):
            raise TypeError
        if not isinstance (fname, str):
            raise TypeError
        self.data[url]['f'] = fname
        json.dump(self.data, open(self.archive_json_file, 'w'))

    # Cleaning
    def clean(self, silent = False):
        if not silent: print ('Cleaning...')
        self.clean_json(target = self.archive_json_file, silent=silent)
        self.clean_archive(silent=silent)
        super().clean(silent = silent)
        self.archive_folder = None
        self.data = None
        self.archive_json_file = None
        if not silent: print()

    def clean_archive(self, silent = False):
        for f in glob(os.path.join(self._get_archive_folder(), '*')):
            if not silent: print ('Deleting: ' + f)
            os.remove(f)

class ArticleGetter(ScraperBase):
    article_json_file = None

    def __init__(self, directory = None, silent = False):
        super().__init__(directory, silent)

    def load_json(self, silent = False):
        self.article_json_file = os.path.join(self.directory, 'article.json')

    def load_data_files(self, silent = False):
        if not silent: print ('Loading data files...')
        self._load_article_json(silent = silent)
        if not silent: print ()

    # Articles
    def _load_article_json(self, silent = False):
        super()._load_json(json_file = self.article_json_file, silent = silent)

    def _save_article_url(self, url, fname):
        if not isinstance (url, str):
            raise TypeError
        if not isinstance (fname, str):
            raise TypeError
        self.data[url]['f'] = fname
        json.dump(self.data, open(self.article_json_file, 'w'))

    def _save_article_links(self, url, links):
        if not isinstance (url, str):
            raise TypeError
        if not isinstance (links, list):
            raise TypeError
        self.data[url]['l'] = links
        json.dump(self.data, open(self.article_json_file, 'w'))

    # Cleaning
    def clean(self, silent = False):
        if not silent: print ('Cleaning...')
        self.clean_json(target = self.article_json_file, silent=silent)
        super().clean(silent = silent)
        self.data = None
        self.article_json_file = None
        if not silent: print()

class ArticleScanner(ScraperBase):
    scanned_data = {}
    scanned_json_file = None

    def __init__(self, source = None, directory = None, silent = False):
        super().__init__(directory, silent)

    def load_json(self, silent = False):
        self.scanned_json_file = os.path.join(self.directory, 'scanned.json')

    def load_data_files(self, silent = False):
        if not silent: print ('Loading data files...')
        self._load_scanned_json(silent = silent)
        if not silent: print ()

    # Scanned
    def _load_scanned_json(self, silent = False):
        super()._load_json(json_file = self.scanned_json_file, silent = silent)

    def _save_scanned_links(self, url, links):
        if not isinstance (url, str):
            raise TypeError('url needs to be of type string.')
        if not isinstance (links, list):
            raise TypeError
        self.scanned_data[url] = links
        json.dump(self.scanned_data, open(self.scanned_json_file, 'w'))

    # Cleaning
    def clean(self, silent = False):
        if not silent: print ('Cleaning...')
        try:
            os.remove(
                os.path.join(self._directory, 'archive.json'))
        except:
            pass
        self.clean_json(target = self.scanned_json_file, silent=silent)
        super().clean(silent = silent)
        self.scanned_data = None
        self.scanned_json_file = None
        if not silent: print()

    def get_soup(self, fname, url = 'not supplied', silent = False):
        if fname is None or not isinstance(fname, str):
            raise TypeError("fname must be a string.")
        if url is None or not isinstance(url, str):
            raise TypeError("url must be a string.")
        if not silent:
            print ('Loading & Souping file: [{}] for url: [{}]'.format(
                fname, url))
        try:
            fname = os.path.join(self._get_archive_folder(), fname + '.html')
            with open(fname, 'rb') as fobj:
                return bs(fobj.read(), 'html.parser')
        except FileNotFoundError:
            raise OSError('File not found: {}'.format(fname))

    def find_links_in_page(
            self, url, silent = False,
            target_element = None, target_class = None, target_id = None):
        if not isinstance(url, str): raise TypeError
        fname = self._get_filename(url)
        if target_element is None: target_element = ''
        if not isinstance(target_element, str):
            raise TypeError('Parameter \'target_element\' must be a string.')
        if target_class is None: target_class = ''
        if not isinstance(target_class, str):
            raise TypeError('Parameter \'target_class\' must be a string.')
        if target_id is None: target_id = ''
        if not isinstance(target_id, str):
            raise TypeError('Parameter \'target_id\' must be a string.')

        soup = self.get_soup(fname, silent = silent)
        target = soup.find(target_element, class_=target_class, id=target_id)
        links = []
        for a in target.find_all('a'):
            if a.has_attr('href'):
                link = a.attrs['href'].strip()
                links.append(link)
        self._save_scanned_links(url, links)

    def find_links_in_archive(
            self, silent = False,
            target_element = None, target_class = None, target_id = None):
        for url in set(self.data.keys()):
            if not url in self.scanned_data:
                self.find_links_in_page(
                    url,
                    silent = silent,
                    target_element = target_element,
                    target_class = target_class,
                    target_id = target_id)

    # Analysis
    def count_links(self, counter = None, links = None, domain = None):
        if counter is None: counter = dd(int)
        if links is None:
            links = [_ for key, item in self.data.items()
                     for _ in item['l']]
        if domain is None: domain = 'politics.people.com.cn'
        if not isinstance(domain, str):
            raise TypeError('Parameter \'domain\' must be a string')

        for link in links:
            if domain in link or link[0] == '/':
                counter[link] += 1
            else:
                counter[link] += 1
        return counter

    def get_queue(self, filtr):
        queue = []
        for url, data in self.data.items():
            if url in self.scanned_data:
                queue.extend(data['l'])
        filtr = [_ for _ in queue if filtr in _]
        return filtr


# Feedback
def show_counter(self, counter, filtr = None, silent = False, root = None):
    if not isinstance(root, str):
        raise TypeError('Parameter \'root\' must be a string.')
    if filtr is None:
        filtr = r'/'
        #filtr = r'/[1-2][09][901][0-9]/'
    refiltered_count = {}
    for item in counter:
        if re.search(filtr, item) is not None:
            refiltered_count[item] = counter[item]
    for href, count in sorted(
            refiltered_count.items(),
            key=lambda x: x[1]):
        stripped = href.strip('/').strip('GB/index.html').strip('/')
        if (stripped.endswith('.com') or stripped.endswith('.cn')):
            continue
        if href.startswith('/'):
            if not silent: print ('{:>8} {}'.format(count, root+href))
        else:
            if not silent: print ('{:>8} {}'.format(count, href))

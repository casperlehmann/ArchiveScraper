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

class Agent(object):

    _directory = None
    _archive_folder = None
    _naming_json_file = None
    naming_file_data = None
    _scanned_json_file = None
    scanned_file_data = None

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

    @property
    def naming_json_file(self):
        return self._naming_json_file

    @naming_json_file.setter
    def naming_json_file(self, json_file):
        if not isinstance (json_file, str):
            raise TypeError('naming_json_file must be a string.')
        if len(json_file) == 0:
            raise ValueError('naming_json_file cannot have length zero.')
        self._naming_json_file = json_file

    @property
    def scanned_json_file(self):
        return self._scanned_json_file

    @scanned_json_file.setter
    def scanned_json_file(self, json_file):
        if not isinstance (json_file, str):
            raise TypeError('scanned_json_file must be a string.')
        if len(json_file) == 0:
            raise ValueError('scanned_json_file cannot have length zero.')
        self._scanned_json_file = json_file

    def __init__(
            self, directory = None, naming_json_file = None,
            scanned_json_file = None, silent = False):
        self.directory = directory

        self.naming_json_file = os.path.join(self.directory, naming_json_file)
        self.load_file_names_data_files(silent = silent)

        self.scanned_json_file = os.path.join(self.directory, scanned_json_file)
        self.load_scanned_file_data_files(silent = silent)

    def clean(self, silent = False):
        if not silent: print ('Cleaning...')
        self.delete_file(target = self.naming_json_file, silent=silent)
        self.delete_file(
                target = os.path.join(self._directory, 'archive.json'),
                silent=silent)
        self.delete_file(
                target = os.path.join(self._directory, 'scanned.json'),
                silent=silent)
        self.delete_file(target = self.naming_json_file, silent=silent)
        self.clean_archive(silent=silent)
        for f in glob(os.path.join(self.directory, '*')):
            if not silent: print ('Deleting: ' + f)
            shutil.rmtree(f)
        self.archive_folder = None
        self.file_name_data = None
        self.scanned_file_data = None
        self._naming_json_file = None
        self._scanned_json_file = None
        if not silent: print()

    def clean_archive(self, silent = False):
        for f in glob(os.path.join(self._get_archive_folder(), '*')):
            if not silent: print ('Deleting: ' + f)
            os.remove(f)

    def delete_file(self, target, silent = False):
        try:
            if not silent: print ('Deleting: ' + target + '...')
            os.remove(target)
        except FileNotFoundError:
            if not silent: print ('Does not exist: ' + target)

    def _get_filename(self, url):
        if not isinstance (url, str):
            raise TypeError
        if not url in self.file_name_data:
            raise KeyError('File not registered for url: {}'.format(url))
        fname = self.file_name_data[url]['f']
        return fname

    def _get_filepath(self, url):
        if not isinstance (url, str):
            raise TypeError
        if not url in self.file_name_data:
            raise KeyError
        fname = self._get_filename(url)
        fpath = os.path.join(self._get_archive_folder(), fname)
        if not os.path.isfile(fpath):
            raise OSError(('File {} does not exist.'.format(fname)))
        return fpath

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

    # ScraperBase(object):
    def load_file_names_data_files(self, silent = False):
        if not silent: print ('Loading data files...')
        try:
            self.file_name_data = dd(lambda: dict(), json.load(open(self.naming_json_file)))
        except FileNotFoundError as e:
            if not silent: print ('Creating new file:', self.naming_json_file)
            self.file_name_data = dd(lambda: dict())
            json.dump(self.file_name_data, open(self.naming_json_file, 'w'))
        if not silent: print ()

    # File names and paths
    def _save_filename(self, url, fname):
        if not isinstance (url, str):
            raise TypeError
        if not isinstance (fname, str):
            raise TypeError
        self.file_name_data[url]['f'] = fname
        json.dump(self.file_name_data, open(self.naming_json_file, 'w'))

    # Data
    def load_archive(self, urls, silent = False):
        for url in urls:
            try:
                self.load_archive_page(url, silent = silent)
            except httplib.IncompleteRead as e:
                print (url)
                print (e.partial)

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
            fname = str(len(self.file_name_data)).zfill(6)
            fpath = os.path.join(self._get_archive_folder(), fname)
            with open(fpath, 'wb') as f:
                if not silent: print ('Writing file: {}'.format(fname))
                f.write(url_obj.read())
                self._save_filename(url, fname)

    def load_article_pages(self, *urls, silent = False):
        for url in urls:
            if url in self.file_name_data:
                self._get_filename(url)
                if not silent: print ('Alredy here')
            else:
                self._fetch_article_page(url, silent = silent)
                self._get_filename(url)

    def _fetch_article_page(self, url, silent = False):
        with urllib.request.urlopen(url) as url_obj:
            os.makedirs(os.path.join(self.directory, 'articles'), exist_ok=True)
            fname = str(len(self.file_name_data)).zfill(6)
            with open(fname, 'wb') as f:
                if not silent: print ('Writing file: {}'.format(fname))
                f.write(url_obj.read())
                self._save_filename(url, fname)

    # ScannerBase(object):
    def load_scanned_file_data_files(self, silent = False):
        if not silent: print ('Loading data files...')
        try:
            self.scanned_file_data = dd(lambda: dict(), json.load(open(self.scanned_json_file)))
        except FileNotFoundError as e:
            if not silent: print ('Creating new file:', self.scanned_json_file)
            self.scanned_file_data = dd(lambda: dict())
            json.dump(self.scanned_file_data, open(self.scanned_json_file, 'w'))
        if not silent: print ()

    def _save_links_from_page(self, url, links):
        if not isinstance (url, str):
            raise TypeError('url needs to be of type string.')
        if not isinstance (links, list):
            raise TypeError
        self.scanned_file_data[url] = links
        json.dump(self.scanned_file_data, open(self.scanned_json_file, 'w'))

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
        if target is None: target = soup
        links = []
        for a in target.find_all('a'):
            if a.has_attr('href'):
                link = a.attrs['href'].strip()
                links.append(link)
        self._save_links_from_page(url, links)

    def find_links_in_archive(
            self, silent = False,
            target_element = None, target_class = None, target_id = None):
        for url in set(self.file_name_data.keys()):
            if not url in self.scanned_file_data:
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
            links = [_ for key, item in self.file_name_data.items()
                     for _ in item]
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
        for url, data in self.file_name_data.items():
            if url in self.scanned_file_data:
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

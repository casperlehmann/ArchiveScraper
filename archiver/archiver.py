"""Class for scraping website.

"""

import json
import os
import re
import shutil
import urllib.request
import http.client
import logging

from collections import defaultdict as dd
from socket import timeout
from glob import glob

from bs4 import BeautifulSoup as bs

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Agent(object):
    """Class for scraping website.

    """

    _directory = None
    _archive_folder = None
    _naming_json_file = None
    _scanned_json_file = None
    scanned_file_data = None

    def __init__(
            self, directory = None, naming_json_file = None,
            scanned_json_file = None, archive_folder = None):
        self.directory = directory
        if not archive_folder is None:
            self._archive_folder = os.path.join(self.directory, archive_folder)

        self.naming_json_file = os.path.join(self.directory, naming_json_file)

        self.file_name_data = None
        self.load_file_names_data_files()

        self.scanned_json_file = os.path.join(self.directory, scanned_json_file)
        self.load_scanned_file_data_files()

    @property
    def directory(self):
        """dir"""
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
        """_"""
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
        """_"""
        return self._scanned_json_file

    @scanned_json_file.setter
    def scanned_json_file(self, json_file):
        if not isinstance (json_file, str):
            raise TypeError('scanned_json_file must be a string.')
        if len(json_file) == 0:
            raise ValueError('scanned_json_file cannot have length zero.')
        self._scanned_json_file = json_file

    @property
    def archive_folder(self):
        """_"""
        return self._archive_folder

    @archive_folder.setter
    def archive_folder(self, archive_folder):
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
        os.makedirs(archive_folder, exist_ok=True)
        self._archive_folder = archive_folder

    @staticmethod
    def delete_file(target):
        """_"""
        try:
            logging.info('Deleting: ' + target + '...')
            os.remove(target)
        except FileNotFoundError:
            logging.info('Does not exist: ' + target)

    # Feedback
    @staticmethod
    def show_counter(counter, root, filtr = None):
        """_"""
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
            if stripped.endswith('.com') or stripped.endswith('.cn'):
                continue
            if href.startswith('/'):
                logging.info('%8s %s', count, root+href)
            else:
                logging.info('%8s %s', count, href)

    def clean(self):
        """_"""
        logging.info('Cleaning...')
        self.delete_file(target = self.naming_json_file)
        self.delete_file(target = os.path.join(self._directory, 'archive.json'))
        self.delete_file(target = os.path.join(self._directory, 'scanned.json'))
        self.delete_file(target = self.naming_json_file)
        self.clean_archive()
        for f in glob(os.path.join(self.directory, '*')):
            logging.info('Deleting: %s\n', f)
            shutil.rmtree(f)
        self._archive_folder = None
        self.file_name_data = None
        self.scanned_file_data = None
        self._naming_json_file = None
        self._scanned_json_file = None

    def clean_archive(self):
        """_"""
        for f in glob(os.path.join(self.archive_folder, '*')):
            logging.info('Deleting: ' + f)
            os.remove(f)

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
        fpath = os.path.join(self.archive_folder, fname)
        if not os.path.isfile(fpath):
            raise OSError(('File {} does not exist.'.format(fname)))
        return fpath

    # ScraperBase(object):
    def load_file_names_data_files(self):
        """_"""
        logging.info('Loading data files...')
        try:
            self.file_name_data = dd(
                dict, json.load(open(self.naming_json_file)))
        except FileNotFoundError:
            logging.info('Creating new file: %s\n', self.naming_json_file)
            self.file_name_data = dd(dict)
            json.dump(self.file_name_data, open(self.naming_json_file, 'w'))

    # File names and paths
    def _save_filename(self, url, fname):
        if not isinstance (url, str):
            raise TypeError
        if not isinstance (fname, str):
            raise TypeError
        self.file_name_data[url]['f'] = fname
        json.dump(self.file_name_data, open(self.naming_json_file, 'w'))

    # Data
    def load_archive(self, urls):
        """_"""
        four_o_fours = json.load(
            open(os.path.join(self.archive_folder, '404.json')))
        for url in urls:
            if url in four_o_fours:
                logging.info('400:     %s (Previously checked)', url)
                continue
            try:
                self.load_archive_page(url)
            except urllib.error.HTTPError:
                logging.info('404:     %s', url)
                four_o_fours.append(url)
                json.dump(
                    four_o_fours, open(
                        os.path.join(self.archive_folder, '404.json'),
                        'w'))
                continue
            except http.client.IncompleteRead:
                logging.info('Partial: %s', url)
                #print ('Partial', e.partial)
            except urllib.error.URLError:
                logging.info('fail:   %s', url)
                continue
            except timeout:
                logging.info('retry:  %s', url)
                self.load_archive_page(url)

    def load_archive_page(self, url):
        """_"""
        if not isinstance (url, str):
            raise TypeError('url must be a string')
        try:
            fname = self._get_filename(url)
            logging.info('Alredy here: %s', url)
        except KeyError:
            logging.info('Fetching...: %s', url)
            self._fetch_archive_page(url)
            fname = self._get_filename(url)
        return fname

    def _fetch_archive_page(self, url):
        if not isinstance(url, str):
            raise TypeError('url must be a string.')
        if not url.startswith('http'):
            url = 'http://' + url
        with urllib.request.urlopen(url) as url_obj:
            fname = str(len(self.file_name_data)).zfill(6)
            fpath = os.path.join(self.archive_folder, fname)
            with open(fpath, 'wb') as f:
                logging.info('Writing file: %s', fname)
                f.write(url_obj.read())
                self._save_filename(url, fname)

    def load_article_pages(self, *urls):
        """_"""
        for url in urls:
            if url in self.file_name_data:
                self._get_filename(url)
                logging.info('Alredy here')
            else:
                self._fetch_article_page(url)
                self._get_filename(url)

    def _fetch_article_page(self, url):
        with urllib.request.urlopen(url) as url_obj:
            os.makedirs(os.path.join(self.directory, 'articles'), exist_ok=True)
            fname = str(len(self.file_name_data)).zfill(6)
            with open(fname, 'wb') as f:
                logging.info('Writing file: %s', fname)
                f.write(url_obj.read())
                self._save_filename(url, fname)

    # ScannerBase(object):
    def load_scanned_file_data_files(self):
        """_"""
        logging.info('Loading data files...')
        try:
            self.scanned_file_data = dd(
                dict, json.load(open(self.scanned_json_file)))
        except FileNotFoundError:
            logging.info('Creating new file: %s\n', self.scanned_json_file)
            self.scanned_file_data = dd(dict)
            json.dump(self.scanned_file_data, open(self.scanned_json_file, 'w'))

    def _save_links_from_page(self, url, links):
        if not isinstance (url, str):
            raise TypeError('url needs to be of type string.')
        if not isinstance (links, list):
            raise TypeError
        self.scanned_file_data[url] = links
        json.dump(self.scanned_file_data, open(self.scanned_json_file, 'w'))

    def get_soup(self, fname, url = 'not supplied'):
        """_"""
        if fname is None or not isinstance(fname, str):
            raise TypeError("fname must be a string.")
        if url is None or not isinstance(url, str):
            raise TypeError("url must be a string.")
        logging.info(
            'Loading & Souping file: [%s] for url: [%s]', fname, url)
        try:
            fpath = os.path.join(self.archive_folder, fname)
            with open(fpath, 'rb') as fobj:
                return bs(fobj.read(), 'html.parser')
        except FileNotFoundError:
            raise OSError('File not found: {}'.format(fname))

    def find_links_in_page(
            self, url,
            target_element = None, target_class = None, target_id = None):
        """_"""
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

        soup = self.get_soup(fname)
        target = soup.find(target_element, class_=target_class, id=target_id)
        if target is None: target = soup
        links = []
        for a in target.find_all('a'):
            if a.has_attr('href'):
                link = a.attrs['href'].strip()
                links.append(link)
        self._save_links_from_page(url, links)

    def find_links_in_archive(
            self, target_element = None, target_class = None, target_id = None):
        """_"""
        for url in set(self.file_name_data.keys()):
            if not url in self.scanned_file_data:
                self.find_links_in_page(
                    url,
                    target_element = target_element,
                    target_class = target_class,
                    target_id = target_id)

    # Analysis
    def count_links(self, counter = None, links = None, domain = None):
        """_"""
        if counter is None: counter = dd(int)
        if links is None:
            links = [_ for key, item in self.scanned_file_data.items()
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
        """_"""
        queue = []
        for url, data in self.file_name_data.items():
            if url in self.scanned_file_data:
                queue.extend(data['l'])
        filtr = [_ for _ in queue if filtr in _]
        return filtr

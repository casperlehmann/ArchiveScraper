"""Class for scraping website.

"""

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

import archiver

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Agent(object):
    """Class for scraping website.

    """

    _directories = {
        'directory': None,
        'archive_folder': None,
    }

    def __init__(
            self, directory, archive_folder, db):
        self.directory = directory
        self.archive_folder = archive_folder
        self.db = archiver.DB(path = os.path.join(self.directory, db))

    @property
    def directory(self):
        """dir"""
        return self._directories['directory']

    @directory.setter
    def directory(self, directory):
        if not isinstance (directory, str):
            raise TypeError('directory must be a string.')
        if len(directory) == 0:
            raise ValueError('directory name cannot be "".')
        os.makedirs(directory, exist_ok=True)
        if not os.path.isdir(directory):
            raise ValueError('directory is not a directory.')
        self._directories['directory'] = directory

    @property
    def archive_folder(self):
        """_"""
        return self._directories['archive_folder']

    @archive_folder.setter
    def archive_folder(self, archive_folder):
        archive_folder = os.path.join(self.directory, archive_folder)
        if not isinstance(archive_folder, str):
            raise TypeError(
                'Name of archive folder must be a string, not {}'.format(
                    archive_folder))
        os.makedirs(archive_folder, exist_ok=True)
        self._directories['archive_folder'] = archive_folder

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
        self.delete_file(target = self.db.path)
        # clean archive
        for f in glob(os.path.join(self.archive_folder, '*')):
            logging.info('Deleting (archive): %s', f)
            os.remove(f)
        # remove subfolders
        for f in glob(os.path.join(self.directory, '*')):
            logging.info('Deleting: (dir): %s', f)
            shutil.rmtree(f)
        self._directories = {
            'directory': self.directory,
            'archive_folder': None
        }

    def _get_filepath(self, url):
        if not isinstance (url, str):
            raise TypeError
        fname = self.db.get_filename(url)
        fpath = os.path.join(self.archive_folder, fname)
        if not os.path.isfile(fpath):
            raise OSError(('File {} does not exist.'.format(fname)))
        return fpath

    def seed_archive(self, urls):
        """_"""
        self.db.seed_archive(urls)

    @staticmethod
    def exclusion(url):
        """_"""
        url = url.strip('/')
        if url == '#': return True
        if 'click.ng/params.richmedia' in url: return True
        for ending in ['/index.html', '.com', '.cn']:
            if url.endswith(ending):
                return True
        return False

    # Data
    def load_links(self):
        """_"""
        urls = self.db.get_unfetched_links()
        self.load_pages(urls)

    def load_seeds(self):
        """_"""
        urls = self.db.get_unfetched_seeds()
        self.load_pages(urls)

    def load_pages(self, urls):
        """_"""
        for url in urls:
            if self.exclusion(url):
                continue
            if self.db.is_four_o_four(url):
                logging.info('400:     %s (Previously checked)', url)
                continue
            try:
                self.load_page(url)
            except urllib.error.HTTPError:
                logging.info('404:     %s', url)
                self.db.set_four_o_four(url)
                continue
            except http.client.IncompleteRead:
                logging.info('Partial: %s', url) # e.partial
            except urllib.error.URLError:
                logging.info('fail:    %s', url)
                continue
            except timeout:
                logging.info('timeout: %s', url)
                continue
            except ConnectionResetError:
                logging.info(
                    'ConnectionResetError: [Errno 54] Connection reset by peer: %s', url)

    def load_page(self, url):
        """_"""
        if not isinstance (url, str):
            raise TypeError('url must be a string')
        try:
            fname = self.db.get_filename(url)
            logging.info('Alredy here: %s', url)
        except KeyError:
            logging.info('Fetching...: %s', url)
            self._fetch_page(url)
            fname = self.db.get_filename(url)
        return fname

    def _fetch_page(self, url):
        if not isinstance(url, str):
            raise TypeError('url must be a string.')
        if not url.startswith('http'):
            url = 'http://' + url
        with urllib.request.urlopen(url) as url_obj:
            fname = self.db.set_filename(url)
            fpath = os.path.join(self.archive_folder, fname)
            with open(fpath, 'wb') as f:
                logging.info('Writing file: %s', fname)
                f.write(url_obj.read())
            self.db.update_fetched(url)

    def _save_links_from_page(self, url, links):
        if not isinstance (url, str):
            raise TypeError('url needs to be of type string.')
        if not isinstance (links, list):
            raise TypeError
        self.db.set_scanned(url)
        self.db.register_links(url, links)

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
        if not isinstance(url, str):
            raise TypeError('url is type:', type(url), url)
        fname = self.db.get_filename(url)
        if target_element is None: target_element = ''
        if not isinstance(target_element, str):
            raise TypeError('Parameter \'target_element\' must be a string.')
        if target_class is None: target_class = ''
        if not isinstance(target_class, str):
            raise TypeError('Parameter \'target_class\' must be a string.')
        if target_id is None: target_id = ''
        if not isinstance(target_id, str):
            raise TypeError('Parameter \'target_id\' must be a string.')

        soup = self.get_soup(fname, url = url)
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
        for url in self.db.get_unscanned():
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
            links = self.db.get_all_links()
        if domain is None: domain = 'politics.people.com.cn'
        if not isinstance(domain, str):
            raise TypeError('Parameter \'domain\' must be a string')

        for link in links:
            if domain in link or link[0] == '/':
                counter[link] += 1
            else:
                counter[link] += 1
        return counter

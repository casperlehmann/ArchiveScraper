"""Class for scraping website.

"""

import os
import re
import urllib.request
import http.client
import logging

from socket import timeout
from bs4 import BeautifulSoup as bs

import archiver

# pylint: disable=missing-docstring

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Agent(object):
    """Class for scraping website.

    """

    def __init__(self, directory, archive_folder, db):
        self.fh = archiver.FileHander(
            directory = directory, archive_folder = archive_folder, db = db)
        self.db = archiver.DB(path = self.fh.db)

    def clean(self):
        self.fh.clean()

    def get_filepath(self, url):
        if not isinstance (url, str):
            raise TypeError
        fname = self.db.get_filename(url)
        fpath = os.path.join(self.fh.archive_folder, fname)
        if not os.path.isfile(fpath):
            raise OSError(('File {} does not exist.'.format(fname)))
        return fpath

    def seed_archive(self, urls):
        self.db.seed_archive(urls)

    @staticmethod
    def exclusion(url):
        url = url.strip('/')
        if url == '#': return True
        if 'click.ng/params.richmedia' in url: return True
        for ending in ['/index.html', '.com', '.cn']:
            if url.endswith(ending):
                return True
        return False

    # Data
    def load_links(self):
        urls = self.db.get_unfetched_links()
        self.load_pages(urls)

    def load_seeds(self):
        urls = self.db.get_unfetched_seeds()
        self.load_pages(urls)

    def load_pages(self, urls):
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
            fpath = os.path.join(self.fh.archive_folder, fname)
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

    def get_soup(self, url):
        if url is None or not isinstance(url, str):
            raise TypeError("url must be a string.")
        fname = self.db.get_filename(url)
        logging.info(
            'Loading & Souping file: [%s] for url: [%s]', fname, url)
        try:
            fpath = self.get_filepath(url)
            with open(fpath, 'rb') as fobj:
                return bs(fobj.read(), 'html.parser')
        except FileNotFoundError:
            raise OSError('File not found: {}'.format(fname))

    def find_links_in_page(
            self, url,
            target_element = None, target_class = None, target_id = None):
        if not isinstance(url, str):
            raise TypeError('url is type:', type(url), url)
        if target_element is None: target_element = ''
        if not isinstance(target_element, str):
            raise TypeError('Parameter \'target_element\' must be a string.')
        if target_class is None: target_class = ''
        if not isinstance(target_class, str):
            raise TypeError('Parameter \'target_class\' must be a string.')
        if target_id is None: target_id = ''
        if not isinstance(target_id, str):
            raise TypeError('Parameter \'target_id\' must be a string.')

        soup = self.get_soup(url = url)
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
        for url in self.db.get_unscanned():
            self.find_links_in_page(
                url,
                target_element = target_element,
                target_class = target_class,
                target_id = target_id)

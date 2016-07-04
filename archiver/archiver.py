"""Class for scraping website.

"""

import logging

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
            parent = self,
            directory = directory, archive_folder = archive_folder, db = db)
        self.db = archiver.DB(parent = self)
        self.scraper = archiver.Scraper(parent = self)

    def clean(self):
        self.fh.clean()

    def seed_archive(self, urls):
        self.db.seed_archive(urls)

    def load_links(self):
        urls = self.db.get_unfetched_links()
        self.load_pages(urls)

    def load_seeds(self):
        urls = self.db.get_unfetched_seeds()
        self.load_pages(urls)

    def load_pages(self, urls):
        self.scraper.load_pages(urls)

    def _save_links_from_page(self, url, links):
        if not isinstance (url, str):
            raise TypeError('url needs to be of type string.')
        if not isinstance (links, list):
            raise TypeError
        self.db.set_scanned(url)
        self.db.register_links(url, links)

    def find_links_in_archive(
            self, target_element = None, target_class = None, target_id = None):
        for url in self.db.get_unscanned():
            self.find_links_in_page(
                url,
                target_element = target_element,
                target_class = target_class,
                target_id = target_id)

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

    def get_soup(self, url):
        if url is None or not isinstance(url, str):
            raise TypeError("url must be a string.")
        fname = self.db.get_filename(url)
        logging.info(
            'Loading & Souping file: [%s] for url: [%s]', fname, url)
        try:
            fpath = self.db.get_filepath(url)
            with open(fpath, 'rb') as fobj:
                return bs(fobj.read(), 'html.parser')
        except FileNotFoundError:
            raise OSError('File not found: {}'.format(fname))

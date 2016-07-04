""" File analysis.

"""

import logging
import re

from bs4 import BeautifulSoup as bs

# pylint: disable=missing-docstring

class Analyzer():

    def __init__(self, parent):
        self.parent = parent

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

    def find_text_in_page(self, url):
        if not isinstance(url, str):
            raise TypeError('url is type:', type(url), url)
        soup = self.get_soup(url = url)
        return soup.text

    def get_soup(self, url):
        if url is None or not isinstance(url, str):
            raise TypeError("url must be a string.")
        fname = self.parent.db.get_filename(url)
        logging.info(
            'Loading & Souping file: [%s] for url: [%s]', fname, url)
        try:
            fpath = self.parent.db.get_filepath(url)
            with open(fpath, 'rb') as fobj:
                soup = bs(fobj.read(), 'html.parser')
                # Remove all scripts and style data:
                # http://stackoverflow.com/questions/22799990/beatifulsoup4
                #                       -get-text-still-has-javascript
                for script in soup(["script", "style"]):
                    script.extract()
                return soup
        except FileNotFoundError:
            raise OSError('File not found: {}'.format(fname))

    def _save_links_from_page(self, url, links):
        if not isinstance (url, str):
            raise TypeError('url needs to be of type string.')
        if not isinstance (links, list):
            raise TypeError
        self.parent.db.set_scanned(url)
        self.parent.db.register_links(url, links)

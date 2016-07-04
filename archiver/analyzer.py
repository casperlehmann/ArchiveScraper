""" File analysis.

"""

import logging
import re

from bs4 import BeautifulSoup as bs

# pylint: disable=missing-docstring

class Analyzer():
    def __init__(self):
        pass

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

    def find_links_in_page(self, url, target_element, target_class, target_id):
        soup = self.get_soup(url = url)
        target = soup.find(target_element, class_=target_class, id=target_id)
        if target is None: target = soup
        links = []
        for a in target.find_all('a'):
            if a.has_attr('href'):
                link = a.attrs['href'].strip()
                links.append(link)
        self._save_links_from_page(url, links)

    @staticmethod
    def get_soup(url):
        """_"""
        if url is None or not isinstance(url, str):
            raise TypeError("url must be a string.")
        fname = self.db.get_filename(url)
        fpath = self.get_filepath(url)
        logging.info('Loading & Souping file: [%s] for url: [%s]', fname, url)
        try:
            with open(fpath, 'rb') as fobj:
                return bs(fobj.read(), 'html.parser')
        except FileNotFoundError:
            raise OSError('File not found: {}'.format(fpath))

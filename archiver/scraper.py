""" Web scraping.

"""

import logging
import os
import urllib.request
import http.client

from socket import timeout

# pylint: disable=missing-docstring

class Scraper():
    def __init__(self, parent):
        self.parent = parent

    def load_pages(self, urls):
        for url in urls:
            if self.exclusion(url):
                continue
            if self.parent.db.is_four_o_four(url):
                logging.info('PrevCheck404:%s', url)
                continue
            try:
                self.load_page(url)
            except urllib.error.HTTPError:
                logging.info('404:         %s', url)
                self.parent.db.set_four_o_four(url)
                continue
            except http.client.IncompleteRead:
                logging.info('Partial:     %s', url) # e.partial
            except urllib.error.URLError:
                logging.info('fail:        %s', url)
                continue
            except timeout:
                logging.info('timeout:     %s', url)
                continue
            except ConnectionResetError:
                logging.info(
                    'ConnectionResetError: [Errno 54] Connection reset by peer: %s', url)

    def load_page(self, url):
        if not isinstance (url, str):
            raise TypeError('url must be a string')
        try:
            fname = self.parent.db.get_filename(url)
            logging.info('Alredy here: %s', url)
        except KeyError:
            logging.info('Fetching...: %s', url)
            self._fetch_page(url)
            fname = self.parent.db.get_filename(url)
        return fname

    def _fetch_page(self, url):
        if not isinstance(url, str):
            raise TypeError('url must be a string.')
        if not url.startswith('http'):
            url = 'http://' + url
        fname = None
        try:
            with urllib.request.urlopen(url) as url_obj:
                fname = self.parent.db.set_filename(url)
                fpath = os.path.join(self.parent.fh.archive_folder, fname)
                with open(fpath, 'wb') as f:
                    logging.info('Writing file: %s', fname)
                    f.write(url_obj.read())
                self.parent.db.update_fetched(url)
        except KeyboardInterrupt:
            if not fname is None:
                fname = self.parent.db.get_filename(url)
                # Skip a line to not get annoyed at the interupt formatting.
                print()
                logging.info(
                    'Aborting filename: %s. The number will be skipped.', fname)
                logging.info(
                    'The current url will be fetched next time the script is '
                    'run: %s', url)
                os.remove(os.path.join(self.parent.fh.archive_folder, fname))
                self.parent.db.update_fetched(url, revert = True)
                self.parent.db.rm_filename(url)
                # We COULD decrease the ID in the database, but that is not
                # really good practice.
                # http://stackoverflow.com/questions/9630004/how-to-decrease
                #       -the-auto-increment-id-in-android-sqlite
            exit()

    @staticmethod
    def exclusion(url):
        url = url.strip('/')
        if url == '#': return True
        if 'click.ng/params.richmedia' in url: return True
        for ending in ['/index.html', '.com', '.cn']:
            if url.endswith(ending):
                return True
        return False


""" Web scraping.

"""

import logging
import os
import urllib.request
import http.client

from socket import timeout
from shutil import copyfile

# pylint: disable=missing-docstring

class Scraper():
    def __init__(self, parent):
        self.parent = parent

    def load_pages(self, urls, restorer = None):
        for url in urls:
            if not restorer is None:
                if not url in restorer:
                    logging.info('Skipping url not in restorer.')
                    continue
            if self.exclusion(url):
                continue
            if self.parent.db.is_four_o_four(url):
                logging.info('PrevCheck404:%s', url)
                continue
            try:
                self.load_page(url, restorer)
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

    def load_page(self, url, restorer = None):
        if not isinstance (url, str):
            raise TypeError('url must be a string')
        try:
            fname = self.parent.db.get_filename(url)
            logging.info('Alredy here: %s', url)
        except KeyError:
            self._fetch_page(url, restorer)
            fname = self.parent.db.get_filename(url)
        return fname

    def _fetch_page(self, url, restorer = None):
        if restorer is None: restorer = dict()
        if not isinstance(url, str):
            raise TypeError('url must be a string.')
        if not url.startswith('http'):
            url = 'http://' + url
        fname = None
        try:
            if url in restorer:
                fname = self.parent.db.set_filename(url)
                fpath = os.path.join(self.parent.fh.archive_folder, fname)
                old_file = restorer[url]
                os.makedirs('data_old', exist_ok=True)
                old_file_path = os.path.join('data_old/archives', old_file)
                logging.info('url: %s', url)
                logging.info('Copying file: %s -> %s', old_file, fname)
                copyfile(old_file_path, fpath)
                self.parent.db.update_fetched(url)
            else:
                logging.info('Fetching...: %s', url)
                with urllib.request.urlopen(url) as url_obj:
                    fname = self.parent.db.set_filename(url)
                    fpath = os.path.join(self.parent.fh.archive_folder, fname)
                    with open(fpath, 'wb') as f:
                        logging.info('Writing file: %s', fname)
                        f.write(url_obj.read())
                    self.parent.db.update_fetched(url)
                    if fname == '050000':
                        exit()
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
        if 'click.ng/params.richmedia' in url:
            return True
        for ending in ['/index.html', '.com', '.cn']:
            if url.endswith(ending):
                return True
        return False


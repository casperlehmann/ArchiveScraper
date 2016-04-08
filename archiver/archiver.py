import urllib, re, json
from collections import defaultdict as dd
import numpy as np
import os
from glob import glob

# https://www.reddit.com/r/Python/comments/2uc7y5/greek_letters_in_matplotlib/
import matplotlib
from matplotlib.font_manager import FontProperties
fp = FontProperties('Simsun', 'normal', weight=14)
#plt.xlabel('This is a test 古', fontproperties=fp)

# http://matplotlib.org/examples/pylab_examples/tex_unicode_demo.html
#matplotlib.rcParams['text.usetex'] = True
#matplotlib.rcParams['text.latex.unicode'] = True
#import matplotlib.pyplot as plt

from bs4 import BeautifulSoup as bs
#%matplotlib inline

import datetime

def get_date_as_string_YYYY_mm_dd(date):
    if not isinstance (date, datetime.datetime):
        raise TypeError
    return '{}-{}-{}'.format(
        date.year,
        str(date.month).zfill(2),
        str(date.day).zfill(2))

def get_date_as_string_YYYYmmdd(date):
    if not isinstance (date, datetime.datetime):
        raise TypeError
    return '{}{}{}'.format(
        date.year,
        str(date.month).zfill(2),
        str(date.day).zfill(2))

def get_date_string_generator(
        from_date = 'today',
        earliest_date = '2010-01-01',
        date_formatter = get_date_as_string_YYYYmmdd):
    earliest_date = get_date(earliest_date)
    earliest_date = date_formatter(earliest_date)
    from_date = get_date(from_date)
    i = 0
    while True:
        date = from_date - datetime.timedelta(days=i)
        date_string = date_formatter(date)
        yield date_string
        i += 1
        if earliest_date == date_string:
            break

def get_date(date_string):
    if not isinstance (date_string, str):
        raise TypeError
    if not (date_string == 'today' or
            re.match(r'\d\d\d\d-\d\d-\d\d', date_string)):
        raise ValueError
    if date_string == 'today': date_string = datetime.datetime.today()
    else: date_string = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    return date_string

def get_archive_urls(from_date='today', earliest_date='2012-02-06', url='{}'):
    if not isinstance (from_date, str):
        raise TypeError
    if not (from_date == 'today' or
            re.match(r'\d\d\d\d-\d\d-\d\d', from_date)):
        raise ValueError
    if not isinstance (earliest_date, str):
        raise TypeError
    if not re.match(r'\d\d\d\d-\d\d-\d\d', earliest_date):
        raise ValueError

    get_date(from_date)
    out = []
    for date in get_date_string_generator(
            from_date=from_date,
            earliest_date=earliest_date):
        out.append(url.format(date))
    return out

class Dearchiver(object):
    """Starts from a list of archieve urls and crawls links.

    """

    directory = 'data_dearchiver'
    archive_folder = None
    archive_meta = None
    article_data = None
    url_queue = []
    pages = []
    scanned = []
    links = {}

    def __init__(self, directory = None, silent = False):
        if directory is not None:
            if not isinstance (directory, str):
                raise TypeError
            if not os.path.isdir(directory):
                raise ValueError
            self.directory = directory
        self.archive_json_file = os.path.join(self.directory, 'archive.json')
        self.scanned_json_file = os.path.join(self.directory, 'scanned.json')
        self.article_json_file = os.path.join(self.directory, 'article.json')
        self._load_archive_json(silent = silent)
        self._load_scanned_json(silent = silent)
        self._load_article_json(silent = silent)

    # JSON
    def _load_archive_json(self, silent = False):
        try:
            self.archive_meta = dd(
                lambda: dict(),
                json.load(open(self.archive_json_file)))
        except FileNotFoundError as e:
            if not silent: print ('Creating new file:', self.archive_json_file)
            self.archive_meta = dd(lambda: dict())
            json.dump(self.archive_meta, open(self.archive_json_file, 'w'))

    def _save_archive_url(self, url, fname):
        if not isinstance (url, str):
            raise TypeError
        if not isinstance (fname, str):
            raise TypeError
        self.archive_meta[url]['f'] = fname
        json.dump(self.archive_meta, open(self.archive_json_file, 'w'))

    def _save_archive_links(self, url, links):
        if not isinstance (url, str):
            raise TypeError
        if not isinstance (links, list):
            raise TypeError
        self.archive_meta[url]['l'] = links
        json.dump(self.archive_meta, open(self.archive_json_file, 'w'))

    # Articles
    def _load_article_json(self, silent = False):
        try:
            self.article_data = dd(
                lambda: dict(),
                json.load(open(self.article_json_file)))
        except FileNotFoundError as e:
            if not silent: print ('Creating new file:', self.article_json_file)
            self.article_data = dd(lambda: dict())
            json.dump(self.article_data, open(self.article_json_file, 'w'))

    def _save_article_url(self, url, fname):
        self.article_data[url]['f'] = fname
        json.dump(self.article_mdata, open(self.article_json_file, 'w'))

    def _save_article_links(self, url, links):
        self.article_data[url]['l'] = links
        json.dump(self.article_data, open(self.article_json_file, 'w'))

    # Scanned
    def _load_scanned_json(self, silent = False):
        try:
            self.scanned = list(json.load(open(self.scanned_json_file)))
        except FileNotFoundError as e:
            if not silent: print ('Creating new file:', self.scanned_json_file)
            self.scanned = []
            json.dump(self.scanned, open(self.scanned_json_file, 'w'))

    def _save_scanned(self, url):
        self.scanned.append(url)
        json.dump(self.scanned, open(self.scanned_json_file, 'w'))

    # Data
    def clean(self, silent = False):
        if not silent: print ('Cleaning...')
        try:
            if not silent: print ('Deleting: ' + self.archive_json_file + '...')
            os.remove(self.archive_json_file)
        except FileNotFoundError:
            if not silent: print (self.archive_json_file, 'does not exist.')
        try:
            if not silent: print ('Deleting: ' + self.article_json_file + '...')
            os.remove(self.article_json_file)
        except FileNotFoundError:
            if not silent: print (self.article_json_file, 'does not exist.')
        try:
            if not silent: print ('Deleting: ' + self.scanned_json_file + '...')
            os.remove(self.scanned_json_file)
        except FileNotFoundError:
            if not silent: print (self.scanned_json_file, 'does not exist.')
        for f in glob(os.path.join(self.directory, '/*/*.html')):
            if not silent: print ('Deleting: ' + f)
            os.remove(f)
        for f in glob(os.path.join(self._get_archive_folder(), '*')):
            if not silent: print ('Deleting: ' + f)
            os.remove(f)
        if not silent: print()

    def load_archive(self, archive):
        for url in archive[:2]:
            self.load_archive_pages(url)

    def load_archive_pages(self, url):
        if not isinstance (url, str):
            raise TypeError('url must be a string')
        try:
            fname = self._get_filename(url)
            print ('Alredy here: {}'.format(url))
        except KeyError:
            print ('Fetching...: {}'.format(url))
            self._fetch_archive_page(url)
            fname = self._get_filename(url)
        return fname

    def _get_archive_folder(self, archive_folder_name = None):
        if not archive_folder_name is None:
            archive_folder_name = archive_folder_name
        elif archive_folder_name is None:
                archive_folder_name = 'archive'
        if not isinstance(archive_folder_name, str):
            raise TypeError(
                'Name of archive folder must be a string, not {}'.format(
                    archive_folder_name))
        self.archive_folder = os.path.join(self.directory, archive_folder_name)
        if not os.path.exists(self.archive_folder):
            os.mkdir(self.archive_folder)
        return self.archive_folder

    def _fetch_archive_page(self, url):
        if not url.startswith('http'):
            url = 'http://' + url
        with urllib.request.urlopen(url) as url_obj:
            fname = os.path.join(
                self._get_archive_folder(),
                str(len(self.archive_meta)).zfill(6) + '.html')
            with open(fname, 'wb') as f:
                print ('Writing file: {}'.format(fname))
                f.write(url_obj.read())
                self._save_archive_url(url, fname)

    def load_article_pages(self, *urls):
        for url in urls:
            if url in self.article_data:
                self._get_filename(url)
                print ('Alredy here')
            else:
                self._fetch_article_page(url)
                self._get_filename(url)

    def _fetch_article_page(self, url):
        with urllib.request.urlopen(url) as url_obj:
            if not os.path.exists(os.path.join(self.directory, 'articles')):
                os.mkdir(os.path.join(self.directory, 'articles'))
            fname = os.path.join(
                self.directory, 'articles',
                str(len(self.article_data)).zfill(6) + '.html')
            with open(fname, 'wb') as f:
                print ('Writing file: {}'.format(fname))
                f.write(url_obj.read())
                self._save_archive_url(url, fname)

    # 
    def _get_filepath(self, url):
        if not isinstance (url, str):
            raise TypeError
        if not url in self.archive_meta:
            raise KeyError
        fname = self._get_filename(url)
        if not os.path.isfile(os.path.join(self._get_archive_folder(), fname)):
            raise IOError(('File {} does not exist.'.format(fname)))
        return os.path.join(self._get_archive_folder(), fname)

    def _get_filename(self, url):
        if not isinstance (url, str):
            raise TypeError
        if not url in self.archive_meta:
            raise KeyError
        fname = self.archive_meta[url]['f']
        return fname

    # Analysis
    def count_links(self, counter = None, links = None, domain = None):
        if counter is None:
            counter = dd(int)
        if links is None:
            #links = {_ for key, item in self.archive_meta.items()
            #        for _ in item['l']}
            links = [_ for key, item in self.archive_meta.items()
                     for _ in item['l']]
        if domain is None: domain = ''
        if domain == '': domain = 'politics.people.com.cn'
        for link in links:
            if domain in link:
                counter[link] += 1
        return counter

    def get_soup(self, fname, url = 'not supplied'):
        if fname is None or not isinstance(fname, str):
            raise TypeError("fname must be a string.")
        if url is None or not isinstance(url, str):
            raise TypeError("url must be a string.")
        print ('Loading & Souping file: [{}] for url: [{}]'.format(fname, url))
        with open(fname, 'rb') as fobj:
            return bs(fobj.read(), 'html.parser')

    def find_links(self):
        for url in set(self.archive_meta.keys()):
            if url in self.scanned: continue
            links = []
            fname = self._get_filename(url)
            for a in self.get_soup(fname).find_all('a'):
                if a.has_attr('href'):
                    link = a.attrs['href'].strip()
                    links.append(link)
            self._save_article_links(url, links)
            self._save_scanned(url)

    def get_queue(self, filtr):
        queue = []
        for url, data in self.archive_meta.items():
            if url in self.scanned:
                queue.extend(data['l'])
        filtr = [_ for _ in queue if filtr in _]
        return filtr

    # Feedback
    def show_counter(self, counter, filtr = None):
        if filtr is None:
            filtr = r'/[1-2][09][901][0-9]/'
        refiltered_count = {}
        for item in counter:
            if re.search(filtr, item) is not None:
                refiltered_count[item] = counter[item]
        for href, count in sorted(
                refiltered_count.items(),
                key=lambda x: x[0]):
            print (href)

if __name__ == '__main__':
    archive = get_archive_urls()

    dearch = Dearchiver(archive)

    #dearch.clean()
    dearch.find_links()
    print( len(dearch.archive_meta))


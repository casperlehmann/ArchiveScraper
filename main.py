import urllib, requests, re, json
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
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup as bs
#%matplotlib inline

import datetime

def get_archive_urls():
    numdays = 5000
    base = datetime.datetime.today()
    out = []
    for date in [base - datetime.timedelta(days=x) for x in range(0, numdays)]:
        date_string = '{}{}{}'.format(date.year, str(date.month).zfill(2), str(date.day).zfill(2))
        out.append('http://politics.people.com.cn/GB/70731/review/{}.html'.format(date_string))
        if '20120206' == date_string:
            return out

class Dearchiver(object):
    """Starts from a list of archieve urls and crawls links.

    """

    archive_json_file = 'data_dearchiver/archive.json'
    scanned_json_file = 'data_dearchiver/scanned.json'
    article_json_file = 'data_dearchiver/article.json'
    archive_meta = None
    article_data = None
    url_queue = []
    pages = []
    scanned = []
    links = {}

    def __init__(self, archive):
        self._load_archive_json()
        self._load_scanned_json()
        self._load_article_json()
        for url in archive[:10]:
            self.load_archive_pages(url)

    # JSON
    def _load_archive_json(self):
        try:
            self.archive_meta = dd(lambda: dict(), json.load(open(self.archive_json_file)))
        except FileNotFoundError as e:
            print ('Creating new file: ' + self.archive_json_file)
            self.archive_meta = dd(lambda: dict())
            json.dump(self.archive_meta, open(self.archive_json_file, 'w'))

    def _save_archive_url(self, url, fname):
        self.archive_meta[url]['f'] = fname
        json.dump(self.archive_meta, open(self.archive_json_file, 'w'))

    def _save_archive_links(self, url, links):
        self.archive_meta[url]['l'] = links
        json.dump(self.archive_meta, open(self.archive_json_file, 'w'))

    # Articles
    def _load_article_json(self):
        try:
            self.article_data = dd(lambda: dict(), json.load(open(self.article_json_file)))
        except FileNotFoundError as e:
            print ('Creating new file: ' + self.article_json_file)
            self.article_data = dd(lambda: dict())
            json.dump(self.article_data, open(self.article_json_file, 'w'))

    def _save_article_url(self, url, fname):
        self.article_data[url]['f'] = fname
        json.dump(self.article_mdata, open(self.article_json_file, 'w'))

    def _save_article_links(self, url, links):
        self.article_data[url]['l'] = links
        json.dump(self.article_data, open(self.article_json_file, 'w'))

    # Scanned
    def _load_scanned_json(self):
        try:
            self.scanned = list(json.load(open(self.scanned_json_file)))
        except FileNotFoundError as e:
            print ('Creating new file: ' + self.scanned_json_file)
            self.scanned = []
            json.dump(self.scanned, open(self.scanned_json_file, 'w'))

    def _save_scanned(self, url):
        self.scanned.append(url)
        json.dump(self.scanned, open(self.scanned_json_file, 'w'))

    # Data
    @classmethod
    def clean(self):
        print ('Cleaning...')
        print ('Deleting: ' + self.archive_json_file)
        os.remove(self.archive_json_file)
        print ('Deleting: ' + self.archive_json_file)
        os.remove(self.article_json_file)
        print ('Deleting: ' + self.scanned_json_file)
        os.remove(self.scanned_json_file)
        for file in glob('data_dearchiver/*/*.html'):
            print ('Deleting: ' + file)
            os.remove(file)
        print()

    def load_archive_pages(self, *urls):
        for url in urls:
            if url in self.archive_meta:
                print ('Alredy here')
                self._get_filename(url)
            else:
                self._fetch_archive_page(url)
                self._get_filename(url)

    def _fetch_archive_page(self, url):
        with urllib.request.urlopen(url) as url_obj:
            if not os.path.exists('data_dearchiver/archive'):
                os.mkdir('data_dearchiver/archive')
            fname = 'data_dearchiver/archive/'+str(len(self.archive_meta)).zfill(6)+'.html'
            with open(fname, 'wb') as f:
                print ('Writing file: {}'.format(fname))
                f.write(url_obj.read())
                self._save_archive_url(url, fname)

    def load_article_pages(self, *urls):
        for url in urls:
            if url in self.article_data:
                print ('Alredy here')
                self._get_filename(url)
            else:
                self._fetch_article_page(url)
                self._get_filename(url)

    def _fetch_article_page(self, url):
        with urllib.request.urlopen(url) as url_obj:
            if not os.path.exists('data_dearchiver/articles'):
                os.mkdir('data_dearchiver/articles')
            fname = 'data_dearchiver/articles/'+str(len(self.article_data)).zfill(6)+'.html'
            with open(fname, 'wb') as f:
                print ('Writing file: {}'.format(fname))
                f.write(url_obj.read())
                self._save_archive_url(url, fname)

    def get_soup(self, url):
        fname = self._get_filename(url)
        if fname is not None:
            print ('Loading & Souping file: {} for url {}'.format(fname, url))
            with open(fname, 'rb') as fobj:
                return bs(fobj.read(), 'html.parser')

    # 
    def _get_filename(self, url):
        fname = self.archive_meta[url]['f']
        if os.path.isfile(fname):
            return fname
        else:
            print ('File {} does not exist.'.format(fname))

    # Analysis
    def count_links(self, counter = None, links = None, domain = None):
        if counter is None:
            counter = dd(int)
        if links is None:
            #links = {_ for key, item in self.archive_meta.items() for _ in item['l']}
            links = [_ for key, item in self.archive_meta.items() for _ in item['l']]
        if domain is None: domain = ''
        if domain == '': domain = 'politics.people.com.cn'
        for link in links:
            if domain in link:
                counter[link] += 1
        return counter

    def find_links(self):
        for url in set(self.archive_meta.keys()):
            if url in self.scanned: continue
            links = []
            for a in self.get_soup(url).find_all('a'):
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
        for href, count in sorted(refiltered_count.items(), key=lambda x: x[0]):
            print (href)


archive = get_archive_urls()

dearch = Dearchiver(archive)

dearch.clean()
dearch.find_links()
print( len(dearch.archive_meta))

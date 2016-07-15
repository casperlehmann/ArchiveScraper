"""Class for scraping website.

"""

import logging

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
        self.analyzer = archiver.Analyzer(parent = self)

    def clean(self):
        self.fh.clean()

    def seed_archive(self, urls):
        self.db.seed_archive(urls)

    def load_unfetched_links(self, restorer = None):
        urls = self.db.get_unfetched_links()
        #exit()
        self.scraper.load_pages(urls, restorer)

    def load_unfetched_seeds(self, restorer = None):
        urls = self.db.get_unfetched_seeds()
        self.scraper.load_pages(urls, restorer)

    def load_pages(self, urls, restorer = None):
        self.scraper.load_pages(urls, restorer)

    def find_links_in_archive(
            self, target_element = None, target_class = None, target_id = None):
        for url in self.db.get_unscanned():
            self.analyzer.find_links_in_page(
                url,
                target_element = target_element,
                target_class = target_class,
                target_id = target_id)

    def extract_text_from_articles(self):
        """Only scan non-seeds.

        """
        fetched_pages = self.db.get_fetched_articles()
        for page in fetched_pages:
            print (''.join((80*['='])))
            print (''.join((80*['='])))
            print ()
            text = self.analyzer.find_text_in_page(page)
            import re
            out = text
            out = re.sub(r'\n+', r'\n', out)
            out = re.sub(r'\t+', r'', out)
            out = re.sub(r'( )+', r' ', out)
            print ('来源 in out and 字号 in out:', '来源' in out and '字号' in out)
            print (out)
            print ()
        #file_names = [self.db.get_filepath(_) for _ in fetched_pages]
        #print (file_names[:10])

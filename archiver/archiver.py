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

    def load_unfetched_links(self):
        urls = self.db.get_unfetched_links()
        self.scraper.load_pages(urls)

    def load_unfetched_seeds(self):
        urls = self.db.get_unfetched_seeds()
        self.scraper.load_pages(urls)

    def load_pages(self, urls):
        self.scraper.load_pages(urls)

    def find_links_in_archive(
            self, target_element = None, target_class = None, target_id = None):
        for url in self.db.get_unscanned():
            self.analyzer.find_links_in_page(
                url,
                target_element = target_element,
                target_class = target_class,
                target_id = target_id)

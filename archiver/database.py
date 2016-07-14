""" Database handler

"""

import os
import logging

import sqlite3 as lite

# pylint: disable=missing-docstring, too-many-public-methods

class DB():

    def __init__(self, parent):
        self.parent = parent
        self.create_name_mapper()
        self.create_links_mapper()

    def create_name_mapper(self):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                'CREATE TABLE IF NOT EXISTS file_names('
                'url VARCHAR(255) NOT NULL,'
                'ID INTEGER PRIMARY KEY AUTOINCREMENT,'
                'scanned INT DEFAULT 0,'
                'four_o_four INT DEFAULT 0'
                ')'
            )

    def create_links_mapper(self):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                'CREATE TABLE IF NOT EXISTS links('
                'url VARCHAR(255) NOT NULL,'
                'link VARCHAR(255) NOT NULL,'
                'fetched INT DEFAULT 0,'
                'UNIQUE(url, link) ON CONFLICT IGNORE'
                ')'
            )

    def connect(self):
        return lite.connect(self.parent.fh.db)

    def drop_name_mapper(self):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute('DROP TABLE file_names')

    def clean(self):
        self.drop_name_mapper()

    def set_filename(self, url):
        if not isinstance (url, str):
            raise TypeError
        with self.connect() as con:
            cur = con.cursor()
            cur.execute('INSERT INTO file_names (url) VALUES (?)', (url,))
            filename = str(cur.lastrowid).zfill(6)
            return filename

    def get_filepath(self, url):
        if not isinstance (url, str):
            raise TypeError
        fname = self.get_filename(url)
        fpath = os.path.join(self.parent.fh.archive_folder, fname)
        if not os.path.isfile(fpath):
            raise OSError(('File {} does not exist.'.format(fname)))
        return fpath

    def get_filename(self, url):
        with self.connect() as con:
            if not isinstance (url, str):
                raise TypeError
            cur = con.cursor()
            cur.execute('SELECT id FROM file_names WHERE url=?', (url,))
            result = cur.fetchone()
            if result is None:
                raise KeyError('File not registered for url: {}'.format(url))
            filename = str(result[0]).zfill(6)
            return filename

    def rm_filename(self, url):
        with self.connect() as con:
            if not isinstance (url, str):
                raise TypeError
            cur = con.cursor()
            cur.execute('DELETE FROM file_names WHERE url=?', (url,))

    def get_unscanned(self):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                'SELECT file_names.url FROM file_names '
                'JOIN links ON file_names.url = links.link '
                'WHERE scanned = 0 AND four_o_four = 0 '
                'AND links.url = "seed"'
            )
            return [_[0] for _ in cur.fetchall()]

    def set_scanned(self, url):
        with self.connect() as con:
            if not isinstance (url, str):
                raise TypeError
            cur = con.cursor()
            cur.execute('UPDATE file_names SET scanned = 1 WHERE url=?', (url,))

    def set_unscanned(self, url):
        """Tell the database that an url has not been scanned for links, e.g.:
        for url in [
                'http://politics.people.com.cn/GB/70731/review/20120216.html',
                'http://politics.people.com.cn/GB/70731/review/20120321.html',
                'http://politics.people.com.cn/GB/70731/review/20120323.html']:
            agent.db.set_unscanned(url)
        """
        with self.connect() as con:
            if not isinstance (url, str):
                raise TypeError
            cur = con.cursor()
            cur.execute('UPDATE file_names SET scanned = 0 WHERE url=?', (url,))

    def register_links(self, url, links):
        with self.connect() as con:
            if not isinstance (url, str):
                raise TypeError
            cur = con.cursor()
            urls = len(links)*[url]
            links = [link if not link.startswith('/')
                     else 'http://'+url[7:].split('/')[0]+link
                     for link in links]
            cur.executemany(
                'INSERT INTO links(url, link) VALUES (?, ?)',
                zip(urls, links))

    def get_all_links(self):
        with self.connect() as con:
            cur = con.cursor()
            return cur.execute('SELECT link FROM links').fetchall()

    def get_four_o_fours(self):
        with self.connect() as con:
            cur = con.cursor()
            res = cur.execute(
                'SELECT url FROM file_names WHERE four_o_four = 1')
            return [_[0] for _ in res.fetchall()]

    def set_four_o_four(self, url):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                'INSERT INTO file_names (url, four_o_four) VALUES (?, 1)',
                (url,))

    def update_fetched(self, url, revert = False):
        fetched = 1-int(revert)
        with self.connect() as con:
            cur = con.cursor()
            cur.execute('UPDATE links SET fetched = ? WHERE url = ?', (fetched, url))

    def is_four_o_four(self, url):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute('SELECT four_o_four FROM file_names WHERE url = ?', (url,))
            res = cur.fetchone()
            if res is None:
                return False
            return bool(res[0])

    def seed_archive(self, urls):
        with self.connect() as con:
            cur = con.cursor()
            cur.executemany(
                'INSERT INTO links (url, link) VALUES (?, ?)',
                zip(len(urls)*['seed'], urls))

    def get_unfetched_seeds(self):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                'SELECT link FROM links WHERE fetched = 0 AND url = "seed"')
            links = {_[0] for _ in cur.fetchall()}
            logging.info(
                'Number of unique links to fetch (archives): %s',
                len(links))
            return links

    def get_unfetched_links(self):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                'SELECT url, link FROM links '
                'WHERE fetched = 0 AND url != "seed"'
            )
            links = {link if not link.startswith('/')
                     else 'http://'+url[7:].split('/')[0]+link
                     for url, link in cur.fetchall()}
            logging.info(
                'Number of unique links to fetch (articles): %s',
                len(links))
            return links

    def get_fetched_articles(self):
        with self.connect() as con:
            cur = con.cursor()
            #cur.execute(
            #    'SELECT file_names.url FROM file_names JOIN links '
            #    'ON file_names.url = links.link ')
            #print (cur.fetchall())

            #cur.execute('SELECT file_names.url FROM file_names')
            #print (cur.fetchall())

            #cur.execute('SELECT link FROM links')
            #print (cur.fetchall())

            cur.execute(
                'SELECT file_names.url FROM file_names JOIN links '
                'ON file_names.url = links.link WHERE links.url != "seed" '
                'AND four_o_four = 0'
            )
            return [_[0] for _ in cur.fetchall()]

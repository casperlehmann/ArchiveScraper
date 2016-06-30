""" Database handler

"""

import sqlite3 as lite

# pylint: disable=missing-docstring

class DB():

    fname = 'data_dearchiver/scraper.db'

    def __init__(self, fname = None):
        if not fname is None: self.fname = fname
        self.create_name_mapper()

    def create_name_mapper(self):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                'CREATE TABLE file_names('
                'url VARCHAR(255) NOT NULL,'
                'ID INTEGER PRIMARY KEY AUTOINCREMENT'
                ')'
            )

    def connect(self):
        return lite.connect(self.fname)

    def drop_name_mapper(self):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute('DROP TABLE file_names')

    def clean(self):
        self.drop_name_mapper()

    def set_filename(self, url):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute('INSERT INTO file_names (url) VALUES ("{}")'.format(url))
            return cur.lastrowid

    def get_filename(self, url):
        with self.connect() as con:
            if not isinstance (url, str):
                raise TypeError
            cur = con.cursor()
            cur.execute('SELECT id FROM file_names WHERE url="{}"'.format(url))
            result = cur.fetchone()
            if result is None:
                raise KeyError('File not registered for url: {}'.format(url))
            filename = str(result[0]).zfill(6)
            return filename

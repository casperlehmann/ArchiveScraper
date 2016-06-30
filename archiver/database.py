""" Database handler

"""

import sqlite3 as lite

# pylint: disable=missing-docstring

class DB():

    fname = 'data_dearchiver/scraper.db'

    def __init__(self, fname = None):
        if not fname is None: self.fname = fname
        with lite.connect(self.fname) as con:
            self.create_name_mapper(con)

    @staticmethod
    def create_name_mapper(con):
        cur = con.cursor()
        cur.execute(
            'CREATE TABLE file_names('
            'url VARCHAR(255) NOT NULL,'
            'ID INTEGER PRIMARY KEY AUTOINCREMENT'
            ')'
        )

    def connect(self):
        return lite.connect(self.fname)

    @staticmethod
    def drop_name_mapper(con):
        cur = con.cursor()
        cur.execute('DROP TABLE file_names')

    def clean(self, con):
        self.drop_name_mapper(con)

    @staticmethod
    def set_filename(con, url):
        cur = con.cursor()
        cur.execute('INSERT INTO file_names (url) VALUES ("{}")'.format(url))
        return cur.lastrowid

    @staticmethod
    def get_filename(con, url):
        if not isinstance (url, str):
            raise TypeError
        cur = con.cursor()
        cur.execute('SELECT id FROM file_names WHERE url="{}"'.format(url))
        result = cur.fetchone()
        if result is None:
            raise KeyError('File not registered for url: {}'.format(url))
        filename = str(result[0]).zfill(6)
        return filename

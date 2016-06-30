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
            'CREATE TABLE name_mapper('
            'url VARCHAR(255) NOT NULL,'
            'ID INTEGER PRIMARY KEY AUTOINCREMENT'
            ')'
        )

    def connect(self):
        return lite.connect(self.fname)

    @staticmethod
    def drop_name_mapper(con):
        cur = con.cursor()
        cur.execute('DROP TABLE name_mapper')

    def clean(self, con):
        self.drop_name_mapper(con)

    @staticmethod
    def insert_url(con, url):
        cur = con.cursor()
        cur.execute('INSERT INTO name_mapper (url) VALUES ("{}")'.format(url))

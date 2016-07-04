""" File handling.

"""

from glob import glob
import logging
import os
import shutil

# pylint: disable=missing-docstring

class FileHander():

    _directory = None
    _archive_folder = None
    _db = None

    def __init__(self, parent, directory, archive_folder, db):
        self.parent = parent
        self.directory = directory
        self.archive_folder = archive_folder
        self.db = db

    @property
    def directory(self):
        """dir"""
        return self._directory

    @directory.setter
    def directory(self, directory):
        if not isinstance (directory, str):
            raise TypeError('directory must be a string.')
        if len(directory) == 0:
            raise ValueError('directory name cannot be "".')
        os.makedirs(directory, exist_ok=True)
        if not os.path.isdir(directory):
            raise ValueError('directory is not a directory.')
        self._directory = directory

    @property
    def archive_folder(self):
        """_"""
        return self._archive_folder

    @archive_folder.setter
    def archive_folder(self, archive_folder):
        archive_folder = os.path.join(self.directory, archive_folder)
        if not isinstance(archive_folder, str):
            raise TypeError(
                'Name of archive folder must be a string, not "{}"'.format(
                    archive_folder))
        os.makedirs(archive_folder, exist_ok=True)
        self._archive_folder = archive_folder

    @property
    def db(self):
        """_"""
        return self._db

    @db.setter
    def db(self, db):
        if not isinstance(db, str):
            raise TypeError(
                'Name of database must be a string, not "{}"'.format(db))
        db = os.path.join(self.directory, db)
        self._db = db

    @staticmethod
    def delete_file(target):
        """_"""
        try:
            logging.info('Deleting: ' + target + '...')
            os.remove(target)
        except FileNotFoundError:
            logging.info('Does not exist: ' + target)

    def clean(self):
        """_"""
        logging.info('Cleaning...')
        self.delete_file(target = self.db)
        # clean archive
        for f in glob(os.path.join(self.archive_folder, '*')):
            logging.info('Deleting (archive): %s', f)
            os.remove(f)
        # remove subfolders
        for f in glob(os.path.join(self.directory, '*')):
            logging.info('Deleting: (dir): %s', f)
            shutil.rmtree(f)
        self.directory = self.directory
        self._archive_folder =  None

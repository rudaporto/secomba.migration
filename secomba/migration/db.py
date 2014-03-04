import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker, mapper
from zope.sqlalchemy import ZopeTransactionExtension

# stub mapper classes

class NewNoticia(object):
    pass

class NewAlbum(object):
    pass

class NewFoto(object):
    pass

class NewMidia(object):
    pass

class NewRelation(object):
    pass


# SQLAlchemy DB Object

class DB(object):
    """DB SQLAlchemy Object"""

    _session = None
    _engine = None
    _meta = None

    def __init__(self):
        self.create_engine()
        self.create_session()
        self.create_tables()
        self.create_mappers()

    @property
    def meta(self):
        return self._meta

    def Session(self):
        """Get session object"""
        return self._session()

    @property 
    def engine(self):
        return self._engine

    def create_engine(self):
        DSN = os.getenv('SECOMDSN', None)
        if DSN is None:
            raise Exception('System environment SECOMDSN is not defined')
        self._engine = create_engine(DSN, convert_unicode=True)

    def create_session(self):
        self._session = scoped_session(sessionmaker(bind=self.engine,
            twophase=True, extension=ZopeTransactionExtension()))

    def create_tables(self):
        self._meta = MetaData(bind=self.engine)
        self.meta.reflect()

    def create_mappers(self):
        mapper(NewNoticia, self.meta.tables['secom_stories'])
        mapper(NewAlbum, self.meta.tables['secom_galeria_evento'])
        mapper(NewFoto, self.meta.tables['secom_galeria_foto'])
        mapper(NewMidia, self.meta.tables['secom_debaser2_files'])
        mapper(NewRelation, self.meta.tables['secom_modules_relationship'])

# -*- coding: utf-8 -*-

from linkedpy import settings
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))


def create_topics_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class Topics(DeclarativeBase):
    """Sqlalchemy topic model"""
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    topic_id = Column('topic_id', Integer, unique=True)
    name = Column('name', String(255))

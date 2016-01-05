from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import settings

DeclarativeBase = declarative_base()

def db_connect():
    return create_engine(URL(**settings.DATABASE))

def create_startupUrls_table(engine):
    DeclarativeBase.metadata.create_all(engine)

class StartupUrls(DeclarativeBase):

    __tablename__ = "StartupUrls"

    id = Column(Integer, primary_key = True)
    url = Column("PathSuffix", String)

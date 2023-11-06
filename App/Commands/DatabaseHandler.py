from sqlalchemy import create_engine, Table, Column, Text, Integer, MetaData
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker, declarative_base

import os

class DatabaseHandler:

    def __init__(self, mainPath) -> None:
        self.databasePath = os.path.abspath(os.path.join(mainPath, "..", "Data", "Database", "ScrapedItems.db"))
        print(self.databasePath)
        self.engine = create_engine("sqlite:///" + self.databasePath)

    def createDatabase(self):
        if not database_exists(self.engine.url):
            create_database(self.engine.url)

            ScrapedInf = Table("ScrapedInf", MetaData(),
                                Column("id", Integer, primary_key=True),
                                Column("content", Text),
                                Column("url", Text),
                                Column("page", Integer),
                                Column("isProcessed", Integer))
            
            ErrorPages = Table("ErrorPages", MetaData(),
                               Column("id", Integer, primary_key=True),
                               Column("url", Text),
                               Column("error", Text),
                               Column("pageNumber", Integer))
            
            ScrapedInf.create(self.engine)
            ErrorPages.create(self.engine)

    def addItemToDatabase(self, content, url, pageNumber):
        Session = sessionmaker(bind=self.engine)
        Base = declarative_base()

        class ScrapedInf(declarative_base()):
            __tablename__ = 'ScrapedInf'

            id = Column(Integer, primary_key=True)
            content = Column(Text)
            url = Column(Text)
            page = Column(Integer)
            isProcessed = Column(Integer)

        Base.metadata.create_all(self.engine)
        session = Session()
        
        new_item = ScrapedInf(content=content, url=url, page=pageNumber, isProcessed=0)
        session.add(new_item)
        session.commit()

    def addErrorPageToDatabase(self, url, error, pageNumber):
        Session = sessionmaker(bind=self.engine)
        Base = declarative_base()

        class ErrorPages(declarative_base()):
            __tablename__ = 'ErrorPages'

            url = Column(Text)
            error = Column(Text)
            pageNumber = Column(Integer)

        Base.metadata.create_all(self.engine)
        session = Session()
        
        new_item = ErrorPages(url=url, error=error, page=pageNumber)
        session.add(new_item)
        session.commit()
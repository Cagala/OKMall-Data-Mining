from sqlalchemy import create_engine, Table, Column, Text, Integer, Date, MetaData, func, text, update
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker, declarative_base

from bs4 import BeautifulSoup
import html5lib

from datetime import datetime

import threading
import re
import os
from time import sleep

from .InsertDataExcel import InsertExcel


class ManageData:

    def __init__(self, mainPath) -> None:
        self.mainPath = mainPath
        self.productDatabasePath = os.path.abspath(os.path.join(mainPath, "..", "Data", "Database", "ProductDatabase.db"))
        self.scrapeDatabasePath = os.path.abspath(os.path.join(mainPath, "..", "Data", "Database", "ScrapedItems.db"))
        self.productEngine = create_engine("sqlite:///" + self.productDatabasePath)
        self.scrapeEngine = create_engine("sqlite:///" + self.scrapeDatabasePath)

        self.MainHandler()

    def MainHandler(self):
        self.createProductDatabase()
        self.getScrapedDatabaseLength()
        
        self.startedTime = datetime.now().strftime("%H:%M:%S")
        self.soupProductContents()
        InsertExcel(self.mainPath)

    def createProductDatabase(self):
        if not database_exists(self.productEngine.url):
                create_database(self.productEngine.url)

                ProductInf = Table("ProductInf", MetaData(),
                                    Column("id", Integer, primary_key=True),
                                    Column("brand", Text),
                                    Column("name", Text),
                                    Column("url", Text),
                                    Column("brackets", Text),
                                    Column("isProcessed", Integer),
                                    Column("processDate", Date))
                
                
                ProductInf.create(self.productEngine)
    
    def getScrapedDatabaseLength(self):
        Session = sessionmaker(bind=self.scrapeEngine)
        Base = declarative_base()

        Base.metadata.create_all(self.scrapeEngine)
        session = Session()

        query = text("SELECT * FROM ScrapedInf WHERE isProcessed = 0")
        dataCount = len(session.execute(query).fetchall())
        self.productUnprocessedLength = dataCount
        self.currentProduct = 1

    def addProductToDatabase(self, brand, name, url, brackets, scrapedID):
        self.currentProduct += 1

        Session = sessionmaker(bind=self.productEngine)
        Base = declarative_base()

        class Product(declarative_base()):
            __tablename__ = 'ProductInf'

            id = Column(Integer, primary_key=True)
            brand = Column(Text)
            name = Column(Text)
            url = Column(Text)
            brackets = Column(Text)
            isProcessed = Column(Integer)
            processDate = Column(Date)
            

        Base.metadata.create_all(self.productEngine)
        session = Session()
        
        new_item = Product(brand=brand, name=name, url=url, brackets=brackets, isProcessed=0, processDate=None)
        session.add(new_item)
        session.commit()
        self.setContentToProcessed(scrapedID)

    def setContentToProcessed(self, scrapedID):
        Session = sessionmaker(bind=self.scrapeEngine)
        Base = declarative_base()

        Base.metadata.create_all(self.scrapeEngine)

        class ScrapedInf(declarative_base()):
            __tablename__ = 'ScrapedInf'

            id = Column(Integer, primary_key=True)
            content = Column(Text)
            url = Column(Text)
            page = Column(Integer)
            isProcessed = Column(Integer)

        session = Session()
        update_product = update(ScrapedInf).where(ScrapedInf.id == scrapedID).values(isProcessed=1)
        
        session.execute(update_product)
        session.commit()
        session.close()



    def getScrapedContents(self):
        Session = sessionmaker(bind=self.scrapeEngine)
        Base = declarative_base()

        Base.metadata.create_all(self.scrapeEngine)

        session = Session()
        query = text("SELECT * FROM ScrapedInf WHERE isProcessed = 0 LIMIT 20")
        results = session.execute(query).fetchall()
        session.close()

        return [[result.id, result.content] for result in results]
    
    def soupProductContents(self):
        while True:
            productContents = self.getScrapedContents()
            
            if not productContents:
                break

            for content in productContents:
                scrapedId = content[0]

                self.printCurrentTask()
                
                soup = BeautifulSoup(content[1], "html5lib") 

                brandName = soup.find("span", {"class": "prName_brand"}).text
                productName = soup.find("span", {"class": "prName_PrName"}).text
                productUrl = "https://www.okmall.com" + soup.find("a", )['href']
                
                matches = re.findall("(\([^)]*\))", productName)
                brackets = ' '.join(matches)
                
                productName = re.sub("(\([^)]*\))", "", productName)
                matches.insert(0, "")
                productName = productName + " ".join(matches)
                
                self.addProductToDatabase(brand=brandName, name=productName, url=productUrl, brackets=brackets, scrapedID=scrapedId)
        self.clearConsole()
        print("\nConverting has ended.")
        print("Converted datas will be inserted to product information...\n")
        sleep(2)

    def clearConsole(self):
        os.system('cls' if os.name == 'nt' else 'clear')    

    def printCurrentTask(self):
        self.clearConsole()
        print("Started Time: ", self.startedTime)
        print("--"*20)
        print(f"{' ':<10}Product Number")
        print(f"{' ':10}{self.currentProduct}")
        print("--"*20)
        print("Current Time: ", datetime.now().strftime("%H:%M:%S"))
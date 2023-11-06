import asyncio
import aiohttp
import html5lib
from bs4 import BeautifulSoup
import re

import logging
from datetime import datetime
from os import name, system
from time import sleep

from .ManageData import ManageData
from .DatabaseHandler import DatabaseHandler

class ScrapingHandler(DatabaseHandler):

    def __init__(self, choice, mainPath) -> None:
        super().__init__(mainPath)
        self.basedUrl = "https://www.okmall.com/products/list?item_type=NEW&search_keyword=&detail_search_keyword=&origin_page=1&page={}"
        self.pageIndex = 0
        self.error = 0
        self.run = True

        self.createDatabase()

        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.MainHandler())
        ManageData(mainPath)
    
    async def MainHandler(self):
        self.startedTime = datetime.now().strftime("%H:%M:%S")

        while self.run:
            self.lastTaskTime = datetime.now().strftime("%H:%M:%S")
            urls = [self.basedUrl.format(self.pageIndex + i) for i in range(1, 6)]
            
            self.printCurrentTask(urls[-1])
            responses = await self.fetchAllUrls(urls)

            self.seperateDatasAndAddToDatabase(responses)

            self.pageIndex += 5
            if self.pageIndex >= 10:
                self.run = False
                
        self.clearConsole()
        print("\nScrapping has ended.")
        print("Scraped datas will be converted to product information...\n")
        sleep(1.5)


    def seperateDatasAndAddToDatabase(self, responses):
        try:
            for scrapingInf in responses:
                page_num_regex = re.compile(r"page=(\d+)$")

                if scrapingInf == None:
                    log_file = "appError.log"
                    logging.basicConfig(filename=log_file, level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

                    logging.error("None Error", exc_info=True)
                    pass
                if scrapingInf != "Error" and scrapingInf != "End" and scrapingInf:
                    items = scrapingInf[0]
                    url = scrapingInf[1]
                    page = page_num_regex.search(url).group(1)
                    for scrapingItem in items:
                        self.addItemToDatabase(str(scrapingItem), str(url), int(page))
                elif scrapingInf == "Error":
                    errorInformations = items[1]

                    errorUrl = errorInformations[0]
                    error = errorInformations[1]
                    errorPageNumber = errorInformations[2]
                    
                    self.error += 1
                    self.addErrorPageToDatabase(errorUrl, error, errorPageNumber)
                else:
                    self.run = False
                    break
        except Exception as e:
            self.addErrorPageToDatabase(responses, e, responses)
            print(e)

    async def fetchAllUrls(self, urls):
        htmls = []

        async def fetchAndScrapePage(session, triedCount, url):
            async with session.get(url) as response:

                try:
                    response.raise_for_status()
                    content = await response.content.read()

                except aiohttp.ClientResponseError as e:
                    if triedCount != 5:
                        await fetchAndScrapePage(session, triedCount+1, url)    
                    else:
                        page_num_regex = re.compile(r"page=(\d+)$")
                        page = page_num_regex.search(url).group(1)
                        print(f"Error while fetching : {e}")
                        return ["Error", [url, str(e), page]]
                    
                except aiohttp.ClientError as e:
                    if triedCount != 5:
                        await fetchAndScrapePage(session, triedCount+1, url)    
                    else:
                        page_num_regex = re.compile(r"page=(\d+)$")
                        page = page_num_regex.search(url).group(1)
                        print(f"Error while fetching : {e}")
                        return ["Error", [url, str(e), page]]

                try:      
                    soup = BeautifulSoup(content, "html5lib")
                    checkItemBox = soup.find_all("div", {"class": "item_box"} )
                    if checkItemBox is None or content is None:
                        if triedCount != 5:
                            await fetchAndScrapePage(session, triedCount+1, url)    
                        else:
                            page_num_regex = re.compile(r"page=(\d+)$")
                            page = page_num_regex.search(url).group(1)
                            print(f"Error while fetching : NoneType object")
                            return ["Error", [url, "NoneType object", page]]
                    elif checkItemBox:
                        return [checkItemBox, url]
                    else:
                        return "End"
                    
                except Exception as e:
                    if triedCount != 5:
                        await fetchAndScrapePage(session, triedCount+1, url)    
                    else:
                        page_num_regex = re.compile(r"page=(\d+)$")
                        page = page_num_regex.search(url).group(1)
                        print(f"Error while fetching : ")
                        return ["Error", [url, e, page]]

        cookies = {"User-Agent":"YOUR USER AGENT"}
        async with aiohttp.ClientSession(cookies=cookies) as session:
            tasks = [fetchAndScrapePage(session, 1, url) for url in urls]
            responses = await asyncio.gather(*tasks)

            htmls.extend(iter(responses))
            return htmls



    
    def clearConsole(self):
        system('cls' if name == 'nt' else 'clear')         
    
    def printCurrentTask(self, url):
        self.clearConsole()
        print(f"Product count is limited for demo")
        print("Started Time: ", self.startedTime)
        print("--"*20)
        print(f"{' ':<10}Page{' ':<10}Error")
        print(f"{' ':10}{self.pageIndex}-{self.pageIndex+5}{' ':<12}{self.error}")
        print("--"*20)
        print("Previous Task: ", self.lastTaskTime)
        print("Current Time: ", datetime.now().strftime("%H:%M:%S"))
        print(url)
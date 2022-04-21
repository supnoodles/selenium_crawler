import concurrent.futures
from .core.websites import GlobalScrape
from typing import Type

class MultiInstance():

    def __init__(self, multi_dic: dict[Type[GlobalScrape], str]) -> None:
        """
        ----- Parameters -----
        multi_dic: dictionary where keys are subclasses of GlobalScrape, and values are destination urls
        ----------------------
        """
        self.multi_dic = multi_dic
        self.drivers = list(self.multi_dic.keys())
        self.urls = list(self.multi_dic.values())

    def multi_scrape(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for key,value in self.multi_dic.items():
                self.threads = executor.submit(key.main, value)
            for thread in self.lst:
                thread.result()

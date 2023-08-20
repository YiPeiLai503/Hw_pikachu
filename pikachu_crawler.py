# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:59:37 2023

@author: L
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import urllib.parse
from bs4 import BeautifulSoup
from requests_html import HTML

class initialize:
    def __init__(self):
        self.__query = '%E7%9A%AE%E5%8D%A1%E4%B8%98'
        self.__imgSearchPrefix = 'https://www.google.com/search?q='
        self.__imgSearchSuffix = '&tbm=isch'
    
    def getQuery(self):
        return self.__query
    
    def setQuery(self, newQuery):
        self.__query = urllib.parse.quote(newQuery) 
    
    def getURL(self):
        return self.__imgSearchPrefix + self.__query + self.__imgSearchSuffix

class imgCrawler:
    def __init__(self):
        self.__count = 4
    
    def setCount(self, value):
        self.__count = value

testURL = 'https://www.google.com/search?q=%E7%9A%AE%E5%8D%A1%E4%B8%98&tbm=isch'

options = Options()
options.add_argument("--disable-notifications")
options.add_argument("--headless")

chrome = webdriver.Chrome(options = options)
chrome.get(testURL)

for i in range(0, 5):
    chrome.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(5)

soup = BeautifulSoup(chrome.page_source, 'html.parser')

img_Tags = soup.find_all('img', {'class':'rg_i Q4LuWd'})

img_link = list()
for tag in img_Tags:
    if tag.get('src') != None:
        img_link.append(tag.get('src'))
    else:
        img_link.append(tag.get('data-src'))
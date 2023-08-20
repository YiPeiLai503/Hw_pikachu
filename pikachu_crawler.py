# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:59:37 2023

@author: L
"""
"""
程式說明:
    使用程式爬取google圖片，並將爬取結果作兩個處理:
        1. 將爬取到的圖片連結寫入 csv 檔，儲存於指定資料夾
        2. 將圖片下載，儲存於指定資料夾
"""

import os
import re
import time
import imghdr
import base64
import pandas as pd
import requests
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

'''
initialize: 爬蟲前參數及工具的設定

__init__:
    query - 查詢目標
    imgSearchPrefix - 完整url中從頭到query前的一段
    imgSearchSuffix - 完整url中從query到尾的一段
    options - 用來設定webdriver的參數

getQuery:
    取得 self.__query 值

setQuery:
    傳入值為中文/英文，透過 urllib.parse.quote 進行編碼轉換成 url 中所需之參數

getURL:
    回傳完整的 url

getDriver:
    設定並回傳 webdriver.Chrome
    參數中的 --disable-notification 為禁用 chrome 的通知功能，使彈跳視窗不會彈跳出來
    參數中的 --headless 為隱藏網頁，運作時瀏覽器會在背景執行
'''
class initialize:
    def __init__(self):
        self.__query = '%E7%9A%AE%E5%8D%A1%E4%B8%98'
        self.__imgSearchPrefix = 'https://www.google.com/search?q='
        self.__imgSearchSuffix = '&tbm=isch'
        self.__options = Options()
        
    def getQuery(self):
        return self.__query
    
    def setQuery(self, newQuery):
        self.__query = urllib.parse.quote(newQuery) 
    
    def getURL(self):
        return self.__imgSearchPrefix + self.__query + self.__imgSearchSuffix
    
    def getDriver(self):
        self.__options.add_argument("--disable-notification")
        self.__options.add_argument("--headless")
        return webdriver.Chrome(options = self.__options)

'''
googleImgCrawler: 爬蟲時的工具設定，最終結果會獲得圖片的 url list

__init__:
    self.__chrome: 爬蟲使用到的瀏覽器，在 initialize 進行過設定，直接傳進來這裡做使用
    self.__loadMore: 爬取的頁面拉到底時，如果還能載入更多，需要按下按鈕才能繼續，這個值為「載入更多」的語法
    　　　　　　　　　這個參數值可以在網頁中先找到按鈕的區塊，接著按下右鍵複製 XPATH 取得
    self.__regularFindstatus: 檢測是否拉到底的匹配文字

getScrollHeight:
    回傳網頁拉到底的高度值

scrollPage:
    模擬網頁下拉的動作，設定緩衝為3秒

clickBotton:
    拉到不能動的時候，可能會有「載入更多」的按鈕，此處為模擬滑鼠按按鈕功能

getSoup:
    回傳解析之網頁

dataStatus:
    在網頁程式碼中，尋找能夠代表現在網頁狀態的值
    透過觀察，起始的data_status值為 1
    在頁面還沒拉到最底端(也就是拉到出現「沒有更多資料」時)前，data_status的值為 2
    拉到底後的 data_status值為 3
    這個函式功能為取得 data_status 的值並回傳

getImgLink:
    解析爬取的網頁，我們要尋找的圖片連結在 img 這個區塊之下，class值為 rg_i Q4luWd
    透過觀察，圖片的標籤有兩種，一個為 src，另一個為 data-src
    一個爬取下來的是圖片存在之 url，另一個則是將圖片鑲嵌在網頁上的 64 位元編碼
    將這些存有圖片位置的link儲存到list中並回傳
'''
class googleImgCrawler:
    def __init__(self, chrome):
        self.__chrome = chrome
        self.__loadMore = r'//*[@id="islmp"]/div/div/div/div/div[1]/div[2]/div[2]/input'
        self.__regularFindstatus = 'data-status="\d\"'
        
    def getScrollHeight(self):
        return self.__chrome.execute_script("return document.body.scrollHeight")
    
    def scrollPage(self):
        self.__chrome.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
    
    def clickBotton(self):
        self.__chrome.find_element(By.XPATH, self.__loadMore).click()
    
    def getSoup(self):
        return BeautifulSoup(chrome.page_source, 'html.parser')
    
    def dataStatus(self, soup):
        status = soup.find('div', {'class':'DwpMZe'})
        data_status = re.findall(self.__regularFindstatus, str(status))
        return int(data_status[0].split("=")[-1].replace('"', ''))
    
    def getImgLink(self, soup):
        imgLink = list()
        imgTags = soup.find_all('img', {'class':'rg_i Q4LuWd'})
        
        for tag in imgTags:
            if tag.get('src') != None:
                imgLink.append(tag.get('src'))
            else:
                imgLink.append(tag.get('data-src'))
        return imgLink

'''
dataStorage: 資料儲存

__init__:
    在此，資料儲存的路徑分三個部分:
        1. ./downloadData/ 在與程式碼同一個資料夾中的 downloadData 底下
        2. 路徑中所爬取的圖片名稱
        3. 細分為兩個資料夾，一個是儲存 csv 另一個儲存下載的圖片
        由於路徑只有在儲存資料類型不同時出現分歧，因此將資料夾路徑細分為三個，方便設定

setPathName: 使用要爬取的圖片名稱為資料夾名稱

getPathName: 取得現在設定之儲存路徑中資料夾名稱

getCSVPath: 取得 csv 檔儲存路徑

getPICPath: 取得 image 檔案儲存路徑

checkAndmakeFolder: 檢查儲存路徑的資料夾是否存在，如果不存在就建立

savedwithCSV: 將爬取到的 imgLink 以 csv 格式儲存起來

savedwithPIC: 將爬取到的 imgLink 中的圖片都下載下來
　　　　　    經過觀察，開頭為 data 的即為遷入網頁的圖片，其為 64 位元編碼，使用 base64 套件進行還原即可
             開頭非 data 的是圖片的儲存連結，要用 requests.get方式取得

'''
class dataStorage:
    def __init__(self):
        self.__pathPrefix = "./downloadData/"
        self.__pathName = "pikachu"
        self.__csvPathSuffix = "/csvFile"
        self.__picPathSuffix = "/image"

    def setPathName(self, name):
        self.__pathName = name
    
    def getPathName(self):
        return self.__pathName
    
    def getCSVPath(self):
        return self.__pathPrefix + self.__pathName + self.__csvPathSuffix
    
    def getPICPath(self):
        return self.__pathPrefix + self.__pathName + self.__picPathSuffix
    
    def checkAndmakeFolder(self, path):
        pathList = path.split('/')
        
        for i in range(len(pathList)):
            if i == 0:
                dirPath = pathList[0]
            else:
                dirPath = os.path.join(dirPath, pathList[i])
                if not os.path.exists(dirPath):
                    os.mkdir(dirPath)
                    print("Make ", dirPath, " Done.")
                else:
                    print("Fold ", dirPath, " Exists!")

    def savedwithCSV(self, csvpath, csvName, result):
        filePath = os.path.join(csvpath, csvName)
        saveFile = pd.DataFrame(result)
        saveFile.to_csv(filePath, header=None, index=False)
        print('csvFile saved!')
        
    def savedwithPIC(self, imgpath, imgLink):
        for i in range(len(imgLink)):
            head = imgLink[i].split(":")[0]
            
            if head == 'data':
                fileName = str(i) + '.jpeg'
                storePath = os.path.join(imgpath, fileName)
                imgcode = imgLink[i].split(",")[1]
                image = base64.b64decode(imgcode)
                file = open(storePath, 'wb')
                file.write(image)
                file.close()
            else:
                img = requests.get(imgLink[i])
                if img.status_code == 200:
                    imgType = imghdr.what(None, img.content)
                    fileName = str(i) + '.' + imgType
                    storePath = os.path.join(imgpath, fileName)
                    file = open(storePath, 'wb')
                    file.write(img.content)
                    file.close()
        print('images saved!')
                
if __name__ == '__main__':
    initial = initialize()
    
    # 修改查詢目標
    # 可用可不用，如不用爬取下來的為皮卡丘圖片
    # initial.setQuery("妙蛙種子")
    
    targetURL = initial.getURL()
    chrome = initial.getDriver()
    chrome.get(targetURL)
    googleImg = googleImgCrawler(chrome)
    soup = googleImg.getSoup()
    dataStore = dataStorage()
    
    # 修改儲存資料夾名稱
    # 可用可不用，如不用儲存之第二層資料夾名稱為 pikachu
    # dataStore.setPathName("bulbasaur")
    
    #先取得儲存路徑並確認其已經建立好
    csv_Path = dataStore.getCSVPath()
    pic_Path = dataStore.getPICPath()
    dataStore.checkAndmakeFolder(csv_Path)
    dataStore.checkAndmakeFolder(pic_Path)


    # 爬取圖片，當dataStatus不為 3 時，重複進行畫面下拉的動作
    # 過程中可能出現拉到底的狀況，此時 temp 的值和getScrollHeight取得的值會一樣
    # 當dataStatus值不為 3 且 temp 和 getScrollHeight值一樣時，代表拉到底，且有「載入更多」的按鈕
    while googleImg.dataStatus(soup) != 3:
        temp = googleImg.getScrollHeight()
        googleImg.scrollPage()
        soup = googleImg.getSoup()
        
        if googleImg.getScrollHeight() == temp:
            googleImg.clickBotton()
    
    img_link = googleImg.getImgLink(soup)
    #去除重複的link
    img_link = list(set(img_link))
    
    # 以下兩個可以挑選其中一個使用，或者同時將資料下載，並將連結以 csv 檔方式儲存
    dataStore.savedwithCSV(csv_Path, dataStore.getPathName()+'.csv', img_link)
    dataStore.savedwithPIC(pic_Path, img_link)
    
    
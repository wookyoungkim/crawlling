from bs4 import BeautifulSoup
import urllib.request
import requests
import ssl
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pymysql
import os
ssl._create_default_https_context = ssl._create_unverified_context

categoryURL = []
category = []
store = "daiz"

def scrapURLs(source, url):
    bsObj=BeautifulSoup(source,"html.parser")
    for link in bsObj.find("div", {"class":"category"}).findAll("a"):
        if 'href' in link.attrs:
            keywords = ["Tops", "Pants", "Outer", "Home Wear", "ACC"]
            for x in keywords:
                if x in link.get_text():
                    print(link.attrs['href'])
                    categoryURL.append(link.attrs['href'])
            

def scrolling(driver, url):
    driver.get(url)
    driver.implicitly_wait(2)

    last_height = driver.execute_script("return document.body.scrollHeight")        #마지막 시점의 창 높이     
    SCROLL_PAUSE_TIME = 2

    while True:
        # Scroll down to bottom                                                      
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)           #새 아이템 로딩시까지 2초 기다리기                                           
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight-50);")  #약간 위로올려서 새 아이템 로딩가능하게
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height            
        new_height = driver.execute_script("return document.body.scrollHeight")     #스크롤 후 창 높이 저장

        if new_height == last_height:                                                
            break

        last_height = new_height

def more(driver, url):          #더보기처리
    while True:
        try:
            result = driver.find_element_by_css_selector('div#btn_more a')
            result.send_keys("\n")
            time.sleep(2)
        except: 
            print("break")
            break


def crawllData(bUrl, link, subcat):
    db = pymysql.connect(
        user='root', 
        passwd='root123', 
        host='127.0.0.1', 
        db='crawlling_test', 
        charset='utf8'
    )
    cursor = db.cursor()

    url = bUrl + str(link)
    print('\n\n')
    print(url)

    categoryId = link.replace("/specialStore/daiz2/sub.ssg?ctgId=","").replace("&dispCtgSubIds=", "")
    if int(categoryId) < 60000414176000041417:
        category = ["Men", subcat]
    else: 
        category = ["Women", subcat]

    chromedriver = '/Users/kim-wookyoung/Downloads/chromedriver' # 맥
    driver = webdriver.Chrome(chromedriver)
    scrolling(driver, url)
    req = driver.page_source
    soup=BeautifulSoup(req, 'html.parser')

    data_list = soup.findAll('div', {'class':"tmpl_itemlist"})     #전체 상품 포함 디브 
    product_list = []
    for data in data_list:
        product_list.extend(data.findAll('li', {'class':'cunit_t232'}))     #각 상품 디브 리스트로 저장
        

    for product in product_list:
        img = product.find('a', {"class":"clickable"})
        href = img['href']
        pURL = "http:" + img.find('img', {'class':"i1"})['src']

        desc = product.find('div', {'class':'cunit_info'})
        pname = desc.find('div', {'class':'title'}).find('a', {"class":"clickable"}).find('em', {'class':'tx_ko'}).get_text()
        pname = pname.replace("[데이즈]", "")
        pprice = desc.find('div', {"class":"cunit_price"}).find("em", {'class':'ssg_price'}).get_text()
        pprice = int(pprice.replace(",",""))
        print(pname + ", " + str(pprice))

        sql = 'SELECT * FROM test where prodURL = %s;'
        cursor.execute(sql, (href))     #중복 검사
        result = cursor.fetchone()
        if result == None :
            sql = ' INSERT INTO test(name, price, imageURL, store, category, subcategory, prodURL) VALUES(%s, %s, %s, %s, %s, %s, %s);'
            cursor.execute(sql, (pname, pprice, pURL, store, category[0], category[1], href))
            db.commit()
            driver.quit()


def main():
    base_url = "http://emart.ssg.com/specialStore/daiz2/main.ssg"
    bUrl = "http://emart.ssg.com"
    #context = ssl._create_unverified_context()

    req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req) #, context=context)
    source = html.read()

    bsObj=BeautifulSoup(source,"html.parser")
    for link in bsObj.find("div", {"class":"special_gnb_scr"}).findAll("a"):
        if 'href' in link.attrs:
            keywords = ["상의", "하의", "아우터.자켓"]
            for x in keywords:
                if x in link.get_text():
                    url = link.attrs['href']
                    print(url)
                    crawllData(bUrl, url, x)


if __name__ == "__main__":
    main()
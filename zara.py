from bs4 import BeautifulSoup
import urllib.request
import requests
import ssl
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pymysql
ssl._create_default_https_context = ssl._create_unverified_context

categoryURL = []
store = "zara"

def scrapURLs(source, url):
    bsObj=BeautifulSoup(source,"html.parser")
    for link in bsObj.find("ul", {"class" : "category-menu"}).findAll("a", {"class" : "menu-item__category-link"}, href=re.compile("^(https:)")):
        if 'href' in link.attrs:
            flag = 0
            keywordsToIgnore = ["new", "event", "special", "join", "co-ords", "maternity", "editorial", "trend", "kids", "bags", "shoes", "sustainability", "z-", "baby", "man-l"]
            for x in keywordsToIgnore:
                if x in link.attrs['href']:
                    flag = -1
            if flag == 0:
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


def main():
    db = pymysql.connect(
        user='root', 
        passwd='root123', 
        host='127.0.0.1', 
        db='crawlling_test', 
        charset='utf8'
    )
    cursor = db.cursor()

    base_url = "https://www.zara.com/kr/"
    #context = ssl._create_unverified_context()

    req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req) #, context=context)
    source = html.read()

    scrapURLs(source, base_url)

    for link in categoryURL:
        url = str(link)
        print('\n\n')
        print(url)
        category = url.replace("https://www.zara.com/kr/ko/","").split("-")
        print(category[0] + " " +category[1])

        chromedriver = '/Users/kim-wookyoung/Downloads/chromedriver' # 맥
        driver = webdriver.Chrome(chromedriver)
        scrolling(driver, url)
        req = driver.page_source
        soup=BeautifulSoup(req, 'html.parser')

        data_list = soup.findAll('ul', {'class':"product-list"})     #전체 상품 포함 디브 
        product_list = []
        for data in data_list:
            product_list.extend(data.select("li:not(.marketing-banner, #category-description-top)"))     #각 상품 디브 리스트로 저장
            
            
        count = 0
        for product in product_list:
            href = product.find('a', {'class':'item'})['href']
            img = product.find('img', {'class':'product-media'})
            if img is None:
                img = product.find('video', {'class':'product-media'})
            desc = product.find('div', {'class':'product-info'})
            product_name = desc.find('div', {'class':'product-info-item-name'})
            pname = product_name.find('a').get_text()
            product_price = desc.find('div', {'class':'product-info-item-price'}).find('div', {'class':'_product-price'})
            if product_price is not None:
                pprice = product_price.find('span').get_text()
                pprice = int(pprice.replace(",","").replace("원", ""))
                print(str(count) + " : " + pname + ", " + str(pprice))
                pURL = img['src']


                sql = 'SELECT * FROM test where prodURL = %s;'
                cursor.execute(sql, (href))     #중복 검사
                result = cursor.fetchone()
                if result == None :
                    sql = ' INSERT INTO test(name, price, imageURL, store, category, subcategory, prodURL) VALUES(%s, %s, %s, %s, %s, %s, %s);'
                    cursor.execute(sql, (pname, pprice, pURL, store, category[0], category[1], href))
                    db.commit()

        driver.quit()
    


if __name__ == "__main__":
    main()
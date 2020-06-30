from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import urllib.request
import requests
import ssl
import pymysql

#db connection 정보
db = pymysql.connect(
    user='root', 
    passwd='root123', 
    host='127.0.0.1', 
    db='crawlling_test', 
    charset='utf8'
)
cursor = db.cursor()
#ssl._create_default_https_context = ssl._create_unverified_context

url = 'https://www.stories.com/kr_krw/clothing/all.html'
store = "&otherstories"

chromedriver = '/Users/kim-wookyoung/Downloads/chromedriver' # 맥
driver = webdriver.Chrome(chromedriver)

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

req = driver.page_source
soup=BeautifulSoup(req, 'html.parser')

data_list = soup.findAll('div', {'class':"o-category-listing"})     #전체 상품 포함 디브 

product_list = []
for data in data_list:
    product_list.extend(data.findAll('div', {'class':'o-product'}))     #각 상품 디브 리스트로 저장
    

for product in product_list:
    img = product.find('img', {'class':'default-image'})
    desc = product.find('div', {'class':'description'})
    product_name = desc.find('div', {'class':'product-title'})
    pname = product_name.find('label').get_text()
    pprice = desc.find('label', {'class':'price'}).get_text()
    pprice = int(pprice.replace(",",""))
    print(pname + ", " + str(pprice))
    pURL = img['src']

    sql = ' INSERT INTO prod_info(name, price, imageURL, store) VALUES(%s, %s, %s, %s);'
    cursor.execute(sql, (pname, pprice, pURL, store))
    db.commit()

driver.quit()



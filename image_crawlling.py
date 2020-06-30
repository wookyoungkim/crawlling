from bs4 import BeautifulSoup
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
ssl._create_default_https_context = ssl._create_unverified_context

base_url = "https://www.stories.com/kr_krw/clothing/all.html"
url = "https://image.thehyundai.com/static/image/sect/hnm/"
store = "&otherstories"
#context = ssl._create_unverified_context()

req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req) #, context=context)
source = html.read()

#전체 소스 가져오기
soup = BeautifulSoup(source, "html.parser")
data_list = soup.findAll('div', {'class':"o-category-listing"})     #전체 상품 포함 디브 

count = 1
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

    sql = ' INSERT INTO prod_info(id, name, price, imageURL, store) VALUES(%s, %s, %s, %s, %s);'
    cursor.execute(sql, (count, pname, pprice, pURL, store))
    db.commit()
    count += 1

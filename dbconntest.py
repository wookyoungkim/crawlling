import pymysql

dbconn = pymysql.connect(
    user='root', 
    passwd='wk980903wk', 
    host='127.0.0.1', 
    db='crawlling_test', 
    charset='utf8'
)
cursor = dbconn.cursor(pymysql.cursors.DictCursor)


# -*- coding: utf-8 -*-
import pandas as pd
import MySQLdb
import sys
import sqlalchemy


reload(sys)
sys.setdefaultencoding('gbk')

db = MySQLdb.connect(
        host='localhost',
        user='root',
        passwd='root',
        db='test',
        charset='gbk'
    )
# 使用cursor()方法获取操作游标 
cursor = db.cursor()

# cursor.execute("SELECT * from test123")
# 使用 fetchone() 方法获取一条数据库。
# data = cursor.fetchone()

# print "Database version : %s " % data

def table_exist(db_name,table_name):
    sql = "SELECT table_name FROM information_schema.TABLES WHERE table_name ='yourname'";
    cursor.execute(sql)
    # 使用 fetchone() 方法获取一条数据库。
    data = cursor.fetchone()
    print "Database version : %s " % data
    
# def persistence(dateframe,coreId):
#     
#     pass
# table_exist("test","atble")
# 
# df = pd.read_csv("data/price-data/000002.csv",encoding="gbk",skiprows =1,names=["datetime","coreId","name","close","high","low","open","a","v","b","n","volume","h","j","k","l"])
# df = df.iloc[::-1]
# l = df.get_values()
# for i in l:
#     i[1] = i[1].replace("'","")
# df = pd.DataFrame(l)
# df.rename(columns={'index': 'id'})
# df.columns = ["datetime","coreId","name","close","high","low","open","before_close","Fluctuation","Chg","Turnover_rate","volume","amount","TotleMarket","CirculationMarket","volnum"]
# print df
# df.to_sql("model1",db, flavor='mysql', if_exists='append')


def findLastDay(table_name):
    sql = "select * from %s as m order by m.`index` DESC limit 1" % table_name
    cursor.execute(sql)
    data = cursor.fetchone()
    print data
    return data[1]

if __name__ == '__main__':
    findLastDay('model1')

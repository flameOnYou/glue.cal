# -*- coding: utf-8 -*-
"""
文件记录
从网易财经接口获取所有股票从2000年01月01日到2017年08月04日的所有日成交价格
临时文件保存在./data/ephemeral.data下
最终将数据录入Mongodb数据库
http://quotes.money.163.com/service/chddata.html?code=0601857&start=20071105&end=20150618
"""
import requests as rq
import pandas as pd
import time
import traceback
import os
import logging
import datetime
import json
from pymongo import MongoClient

# 日志配置
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='log/'+os.path.basename(__file__)+'.log',
                    filemode='w')


# mongodb数据库连接
conn = MongoClient('127.0.0.1', 27017)
db = conn['stock']  #连接mydb数据库，没有则自动创建

thread_num = 1
start_date = "20000101"





"""
往mongdb中插入jsonArr
"""


def insert(coreID,JsonArr):
    table = db[str(coreID)]
    print type(JsonArr)
    json_arry = []
    for val in JsonArr:
        timestamps = val['timestamp']
        # 重复的不能插入
        if table.find({"timestamp":timestamps}).count() <= 0:
            json_arry.append(val)
    print "insert:",json_arry
    table.insert(json_arry)

"""
日期Str转时间戳
"""


def get_timestamp(datestr):
    d = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    return int(time.mktime(d.timetuple()))



"""
将文件转入mongodb
"""

def permit_to_mongo(coreid,filepath):
    df = pd.read_csv(filepath,encoding="gbk",skiprows =1,names=["datetime","coreId","name","close","high","low","open","a","v","b","n","volume","h","j","k","l"])
    df = df.iloc[::-1]
    l = df.get_values()
    for i in l:
        i[1] = i[1].replace("'","")
    df = pd.DataFrame(l)
    df.rename(columns={'index': 'id'})
    df.columns = ["datetime","coreId","name","close","high","low","open","before_close","Fluctuation","Chg","Turnover_rate","volume","amount","TotleMarket","CirculationMarket","volnum"]
    # axis=1取行数据，否则取列
    df['timestamp'] = df.apply(lambda x:get_timestamp(x[0]),axis=1)
    jarr = json.loads(df.to_json(orient='records'))
    insert(coreid,jarr)


"""
获取文件最后一行的日期 +1天
"""
def get_table_last_date(coreId):
    table = db[coreId]
    # 1 为升序，-1为降序。找最近时间的一条记录
    if table.find_one() is None:
        # 改表没有记录
        return None
    r = table.find().sort([("timestamp", -1)]).limit(1)
    x = time.localtime(int(r[0]['timestamp']) + 86400)
    timeStr = time.strftime('%Y-%m-%d', x)
    return timeStr

def func(i):
    while l:
        t = time.time()
        try:
            coreId = str(l.pop())
            start = start_date
            end_date = datetime.datetime.now().strftime('%Y%m%d')
            file_path = "data/ephemeral.data/"+coreId+".csv"

            last_date = get_table_last_date(coreId)
            if last_date is not None:
                start = last_date
            market = "0"
            if coreId[0] != "6":
                market = "1"
            url = "http://quotes.money.163.com/service/chddata.html?code="+market+coreId+"&start="+start+"&end="+end_date
            print url
            r = rq.get(url)
            with open(file_path , 'wb') as f:
                f.write(r.content)
                f.close()
            # 获取所有价格,之后的所有计算都是基于这个价格的
            permit_to_mongo(coreId, file_path)
        except Exception, e:
            print 'str(Exception):\t', str(Exception)
            print 'str(e):\t\t', str(e)
            print 'repr(e):\t', repr(e)
            print 'e.message:\t', e.message
            print 'traceback.print_exc():'
            traceback.print_exc()
            print 'traceback.format_exc():\n%s' % traceback.format_exc()
            continue
        print "thread:%s len:%s time:%s.\n" % (i, len(l), time.time() - t),

if __name__ == "__main__":
    # 从文件中读取
    shaidIdList = []
    with open("data/idList.txt") as f:
        for coreId in f.xreadlines():
            ids = coreId.strip()
            shaidIdList.append(ids)
    l = shaidIdList
    threads = []
    import threading

    for i in range(thread_num):
        t = threading.Thread(target=func, args=(i,))
        t.setName(i)
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


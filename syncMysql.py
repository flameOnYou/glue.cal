# -*- coding: utf-8 -*-
"""
同步数据到Msql中
需要现在Mysql中新建数据库stock
从网易财经接口获取所有股票从2000年01月01日到2017年08月04日的所有日成交价格
文件保存在./data/price下
http://quotes.money.163.com/service/chddata.html?code=0601857&start=20071105&end=20150618
"""
import  requests as rq
import time
import traceback
import os
import logging
import datetime
import sys
import MySQLdb
# 日期配置
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='log/'+os.path.basename(__file__)+'.log',
                    filemode='w')
# 线程数量配置
thread_num = 50

# 开始日期
start_date = "20000101"

# Mysql配置
mysql_ip = "127.0.0.1"
mysql_user = "root"
mysql_password = "root"
mysql_dbname = "stock"

# 设定GBK编码格式
reload(sys)
sys.setdefaultencoding('gbk')

# 初始化数据库连接
db = MySQLdb.connect(
    host= mysql_ip,
    user=mysql_user,
    passwd=mysql_password,
    db=mysql_dbname,
    charset='gbk'
)

"""
检测表是否存在
"""

def table_exist(table_name):
    sql = "SELECT table_name FROM information_schema.TABLES WHERE table_name ='%s'" % table_name
    cursor = db.cursor()
    cursor.execute(sql)
    # 使用 fetchone() 方法获取一条数据库。
    data = cursor.fetchone()
    exist = False
    if data is not None:
        exist = True
    return exist


"""
获取某张表的最后的一个日期+1的字符串
格式为 %Y%m%d
如果没有则返回None
"""
def get_table_lastday(table_name):
    last_date = None
    
    if table_exist(table_name) == False:
        print "table is not exist"
        return last_date
    sql = "select * from %s as m order by m.`index` DESC limit 1" % table_name
    cursor.execute(sql)
    data = cursor.fetchone()
    
    if data is not None:
        dateStr = data[1]
        time = datetime.datetime.strptime(dateStr, '%Y-%m-%d')
        time = time + datetime.timedelta(days = 1)
        last_date = time.strftime('%Y%m%d')
    return last_date 


def func(i):
    while l:
        t = time.time()
        try:
            coreId = str(l.pop())
            print coreId[0]
            
            start =  start_date
            nowdt = datetime.datetime.now()
            end_date = nowdt.strftime('%Y%m%d')
            
            # 如果有最新的日期
            last_date = get_table_lastday(coreId)
            if last_date is not None:
                start = last_date
            
            market = "0"
            if coreId[0] != "6":
                market = "1"
            url = "http://quotes.money.163.com/service/chddata.html?code="+market+coreId+"&start="+start+"&end="+end_date
            
            r = rq.get(url)
            with open(file_path , mode) as f:
                f.write(r.content)
                f.close()
            # 获取所有价格,之后的所有计算都是基于这个价格的
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

# if __name__ == "__main__":
# 
#     
#     # 从文件中读取ID列表
#     shaidIdList = []
#     with open("data/idList.txt") as f:
#         for coreId in f.xreadlines():
#             ids = coreId.strip()
#             shaidIdList.append(ids)
#     l = shaidIdList
#     threads = []
#     import threading
# 
#     for i in range(thread_num):
#         t = threading.Thread(target=func, args=(i,))
#         t.setName(i)
#         threads.append(t)
#     for t in threads:
#         t.start()
#     for t in threads:
#         t.join()

if __name__ == "__main__":
    table_exist("test")

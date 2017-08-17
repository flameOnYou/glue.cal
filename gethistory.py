# -*- coding: utf-8 -*-
"""
文件记录
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

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='log/'+os.path.basename(__file__)+'.log',
                    filemode='w')

thread_num = 50
start_date = "20000101"

"""
获取文件最后一行的日期 +1天
"""
def getFileLastDate(filepath):
    last_date = start_date
    with open(filepath, 'r') as f:
        lines = f._readline()
        if len(lines) >= 2:# 大于两行才有日期
            lastline = lines[-1]
            dateStr = lastline.split(',')[0]
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
            file_path = "data/price-data/"+coreId+".csv"
            mode = 'wb'# 默认是重新写入
# #             检测文件是否存在
            
#             if os.path.exists(file_path):
# #                 如果文件存在就读取最后一行的日期，如果读不到就跟文件不存在一样
#                 start = getFileLastDate(file_path)
#                 mode = 'ab'
#             # 6开头的股票代码前面加上0
#             # 其他加上1
            market = "0"
            if coreId[0] != "6":
                market = "1"
            url = "http://quotes.money.163.com/service/chddata.html?code="+market+coreId+"&start="+start+"&end="+end_date
            print url
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


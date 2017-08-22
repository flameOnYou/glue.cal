# -*- coding: utf-8 -*-
"""
从网易财经接口获取所有股票从2000年01月01日到2017年08月04日的所有日成交价格
文件保存在./data/price下
http://quotes.money.163.com/service/chddata.html?code=0601857&start=20071105&end=20150618
"""
import  requests as rq
import time
import traceback
def func(i):
    while l:
        t = time.time()
        try:
            coreId = str(l.pop())
            print coreId[0]
            # 6开头的股票代码前面加上0
            # 其他加上1
            market = "0"
            if coreId[0] != "6":
                market = "1"
            url = "http://quotes.money.163.com/service/chddata.html?code="+market+coreId+"&start=20000101&end=20170804"
            print url
            r = rq.get(url)
            with open("data/price-data/"+coreId+".csv", "wb") as f:
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

    for i in range(10):
        t = threading.Thread(target=func, args=(i,))
        t.setName(i)
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


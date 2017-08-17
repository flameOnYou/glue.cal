# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 16:01:34 2017

@author: songy
"""
import csv
import datetime
from itertools import groupby
import json
import logging
import os
import time
import traceback

import pandas as pd
import sysutils
import tushare as ts


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='log/quant.log',
                    filemode='w')

# logging.debug('This is debug message')
# logging.info('This is info message')
# logging.warning('This is warning message')



# 重复次数
repeatSize = 3
# 获取多少天的数据
TIME_SPACE = 60

# """
# 读取IdList
# """
# def getIdList():
#     idList = ts.get_industry_classified()
#     result = []
#     for val in idList.values:
#         result.append(val[0])
#     with open("idList.txt","w") as f:
#         f.writelines("\n".join(result))
'''
取出第一次过滤值
'''


def getDateFromMarket(id):
    price = {} 
    # 002060
    data = ts.get_hist_data(id)
    for p in data.iterrows():
        # high
        high = float(p[1]['high'])
        # low
        low = float(p[1]['low'])
        price[p[0].encode("utf-8")] = (high + low) / 2
    return price


"""
改良函数,直接从价格组获取中间值
大量遍历,慎用

"""


def getDateFromMarket_New(data):
    price = {}
    for p in data.iterrows():
        # high
        high = float(p[1]['high'])
        # low
        low = float(p[1]['low'])
        price[p[0].encode("utf-8")] = (high + low) / 2
    return price


'''
给出N日前的字符串，遇到周末则往前取一天
n 前几天
madeTime,类型datetime，指定时间
'''

def getTodayStr(n, madeTime=datetime.datetime.now()):
    date = madeTime + datetime.timedelta(days=-n)
    #    周末
    week = date.isoweekday()
    if week == 6 or week == 7:
        date = madeTime + datetime.timedelta(days=-n - 2)
    return date.strftime('%Y-%m-%d')





"""
从 x 天开始 ，往前取N天(不包括周末)
返回dateList [xxx-xx--xx,xxx-xx--xx,xxx-xx--xx,xxx-xx--xx,.....]
"""


def getNdayBefore(madeTime, beforeDate, daterange):
    #    计数标识
    totle = beforeDate
    #    要取的日期date list
    dateList = []
    while len(dateList) <= daterange:
        dateStr = getTodayStr(totle, madeTime)
        #        如果不在列表中
        if dateStr not in dateList:
            dateList.append(dateStr)
        # 如果在列表中
        totle = 1 + totle

    return dateList


"""
price:价格list
madeTime:计算价格的日期 datetime.datetime
moveDate:平移X天
rangeSize:连续 N天的移动平均值
"""


def moveAverage(price, madeTime, moveDate, rangeSize):
    dateList = getNdayBefore(madeTime, moveDate, rangeSize - 1)
    sum_price = 0
    totle = 0
    for date in dateList:
        #        没有找到指定日期的数据,如果所有的数据都没有，就返回异常值
        if date not in price:
            continue
        sum_price = sum_price + price[date]
        totle += 1
    if totle == 0:
        return 0
    return sum_price / totle


"""
计算某日红线的值
price:某股票的所有价格列表
"""


def getRedVal(price, dataStr):
    madeTime = datetime.datetime.strptime(dataStr, '%Y-%m-%d')
    moveDate = 5
    rangeSize = 8
    dateList = getNdayBefore(madeTime, moveDate, rangeSize - 1)
    sum_price = 0;
    totle = 0;
    for date in dateList:
        #        没有找到指定日期的数据,如果所有的数据都没有，就返回异常值
        if date not in price:
            continue
        sum_price = sum_price + price[date]
        totle += 1
    if totle == 0:
        print "totle == 0 ,can find data"
        return 0
    return sum_price / totle


"""
输入时间字符串
输出下一天的字符串，掠过周末
"""


def getNextDate(dataStr, num):
    date_time = datetime.datetime.strptime(dataStr, '%Y-%m-%d')

    oneday = datetime.timedelta(days=num)
    nextData = date_time + oneday
    week = nextData.isoweekday()
    nextDataStr = nextData.strftime('%Y-%m-%d')
    if week == 6 or week == 7:
        return getNextDate(nextDataStr, 1)
    return nextDataStr


"""
查询List中 var连续出现的最大次数
"""


def findRepeatNum(l, var):
    s = [len(list(g)) for k, g in groupby(l) if k == var]
    return max(s) if list(s) else 0


"""
传入价格列表，查询出现连续粘合的最大次数
"""


def ShareWithCondition(price,all_price_data):

    #   往前n天

    #   比较目标
    logging.info("======================粘合计算开始==========================")

    
    #   是否出现粘合的List
    repeat_list = []
    # 出现粘合的日期列表
    glue_list = []
    todayStr = sysutils.get_today_str()
    # 已经计算过的日期
    caling_date = ""
    
    dayAgo = len(all_price_data)
    for i in range(0, dayAgo):
#         print all_price_data()
        # 日期
        timeStr = all_price_data.ix[i].name
#          sysutils.get_nday_before(todayStr,i)
        if timeStr == caling_date:
            continue
        caling_date = timeStr
        orderBase = sysutils.orderBase(all_price_data,timeStr)
        green = sysutils.sma(all_price_data, timeStr, 3, 5)
        red   = sysutils.sma(all_price_data, timeStr, 5, 8)
        blue  = sysutils.sma(all_price_data, timeStr, 8, 13)
        logging.info("[ %s ] ob = %s ,green = %s , red = %s ,blue = %s ,Rg %s ,Rb %s",timeStr,orderBase,green,red,blue,abs(red - green),abs(red - blue))
        if green == 0 or red == 0 or blue == 0:
            # 异常数据就继续
            continue
        if abs(red - green) <= orderBase or abs(red - blue) <= orderBase:
            glue_list.append(timeStr)

    print "glue_list:",glue_list
    logging.info("======================粘合计算结束==========================")
    return glue_list


"""
传入所有出现粘合的日期集合list
返回连续出现3日粘合的日期
"""


def getGlueDate(all_price_data,l):
    result_list = []
    index = 1
    map = {}
    index_list = list(all_price_data.index)
    for dates in l:
        nextdata_index = index_list.index(dates) + 1
        nextdata = all_price_data.ix[nextdata_index].name
        
        nextdata_index2 = index_list.index(dates) + 2
        next2data = all_price_data.ix[nextdata_index2].name
        
        if nextdata in l and next2data in l and nextdata != next2data:
            map[index] = [dates, nextdata, next2data]
            index += 1

    return map

""""
量化计算(一次三个粘合的价格范围段)
传入参数是dataframe
文件头
股票代码    出现粘合日期  订单状态    进场日期    是否有平半仓  进场价格    出场日期    出场价格     利润

"""


def quantization(coreid,price_flag,all_price_data,startTime,startIndex,endIndex):
    print "init quantization"
    pricedata = all_price_data[startIndex:endIndex]
#     倒序一下,日期从小到大
    priceList = pricedata.iloc[::-1]
#     获取最后三个取出进场点和止损位置
    maxlist = []
    minlist = []
    for ld in priceList[0:2].iterrows():
        high = float('%.3f' % ld[1]['high'])
        low = float('%.3f' % ld[1]['low'])
        maxlist.append(high)
        minlist.append(low)
    # 进场点
    intoPoint = max(maxlist)
    # 止损点
    outPoint = min(minlist)
    # 计算平半仓的点位
    expect_half_price = abs(intoPoint - outPoint)+intoPoint

    # 粘合模型成立，开始走盘

    # 0表示观望,未进场
    # 1:进场做多
    # -1:未进场就被达到止损位置出场
    # 2:止损出场
    # 3:压到红线止损出场
    statusMap = {0: "观望,未进场",1: "进场做多",-1:"未进场就被达到止损位置出场",2: "止损出场",3:"压到红线止损出场"}
    status = 0  # 订单状态,
    isHalf = False  # 是否有机会平一半仓位

    intoTime = ""  # 进场日期
    outofPrice = 0  # 出场价格
    outofTime = ""  # 出场日期
    outlist = [-1, 2, 3]
    for p in priceList[3:].iterrows():
        # 如果订单状态为出场则直接跳出循环
        if status in outlist:
            break
        dataStr = p[0]

        high = float('%.3f' % p[1]['high'])
        low = float('%.3f' % p[1]['low'])

        # 有价格突破进场点,进场
        if status == 0 and high >= intoPoint:
            intoTime = dataStr
            status = 1
            continue
        #     未进场就被达到止损位置出场
        if status == 0 and outPoint <= low:
            status = -1
            break
        # 进场状态
        if status == 1:
            # 红线状态
            red = sysutils.sma(all_price_data, dataStr, 5, 8)
            # 是否有平半仓的机会
            if high >= expect_half_price:
                isHalf = True
            #     止损出场
            if low <= outPoint:
                status = 2
                outofPrice = outPoint
                outofTime = dataStr
                break
            # 压到红线出场
            if low <= red and isHalf == True:
                status = 3
                outofPrice = red
                outofTime = dataStr
                break
    profit = 0
    if status == 2 or status == 3 :
        profit = outofPrice - intoPoint
    # 股票代码	出现粘合日期	订单状态	进场日期	是否有平半仓	进场价格	出场日期	出场价格	 利润
    report = (coreid, startTime, statusMap.get(status), intoTime, isHalf, intoPoint, outofTime,'%.2f' %  outofPrice,'%.2f' % profit)
    file_Address = "data/report.csv"
    mode = "ab+"# 模式ab+,wb表示没有空行
    writeHead = False
    if os.path.isfile(file_Address) == False:
        mode ='wb'
        writeHead = True
    with open(file_Address, mode) as f:
        fp = csv.writer(f)
        if writeHead == True:
            # 写入头部
            fp.writerow(("股票代码","出现粘合日期","订单状态","进场日期","是否有平半仓","进场价格","出场日期","出场价格"," 利润"))
        fp.writerow(report)

    print "dateStr:",startTime,"expect_half_price",expect_half_price,"status:",statusMap.get(status),"isHalf:",isHalf,"outofPrice:",outofPrice,"intoTime",intoTime,"outofTime",outofTime



"""
从文件中获取历史数据
csv文件为gbk编码格式
index_col =0 : 让第一列时间作为索引
skiprows =1 跳过第一行文件头
names=["datetime","coreId","name","close","high","low","open","前收盘","涨跌额","涨跌幅","换手率","成交量","成交金额","总市值","流通市值","成交笔数"])
自定义列名

删除coreId 和 name 让格式和tushare财经包的一样
"""


def read_hit_csv(coreId):
    filename = "data/price-data/"+coreId +".csv"
    df = pd.read_csv(filename,encoding="gbk",index_col =0,skiprows =1,names=["datetime","coreId","name","close","high","low","open","前收盘","涨跌额","涨跌幅","换手率","volume","成交金额","总市值","流通市值","成交笔数"])
    df = sysutils.dfreserve(df)
    return df


"""
从id池拿出一个id去请求,然后计算
"""



def func(i):
    while l:
        t = time.time()
        try:
            shareid = l.pop()
            logging.info("从ID池中取出股票ID [%s] 进行计算",shareid)
            # 获取所有价格,之后的所有计算都是基于这个价格的
            # all_price_data = ts.get_hist_data(shareid)  # 来源于网络的价格，三年

            all_price_data = read_hit_csv(shareid)# 来源于本地价格,十多年
            # logging.info("从文件中获取数据 %s - %s", all_price_data.head(3),all_price_data.tail(3))

            price_flag = getDateFromMarket_New(all_price_data) #  价格标识
            #  价格标识
            glue_list = ShareWithCondition(price_flag,all_price_data)
            if len(glue_list) <= 0:
                continue

            # timeflagList = [[日期1,日期2,日期3],[日期1,日期2,日期3]......]
            timeflagList = getGlueDate(all_price_data,glue_list)
            print "timeflagList:",timeflagList
            # all_result_json_list = []
            for val in timeflagList.values():
                unitMap = {}
                # [股票代码]coreId": "60016",
                unitMap["coreId"] = shareid
                # [粘合均线的开始]timeflag":"2017-1-1",
                unitMap["timeflag"] = val
                # 获取val[0]之后一个月的数据
                startTime = val[0]
                # endTime = getNextDate(startTime,TIME_SPACE)
                # 这个all_price_data是相反的，0的索引是最新的数据
                if startTime not in list(all_price_data.index):
                    logging.info("开始时间未在列表中,数据缺失,不计入量化计算,股票id:"+shareid+"缺失时间:"+startTime)
                    continue
                endIndex = list(all_price_data.index).index(startTime)+1

                startIndex = endIndex - TIME_SPACE
                if startIndex <= 0:
                    startIndex = 0
                pricedata = all_price_data[startIndex:endIndex]
                unit_price_list = []
                red_val_list = []
                # 这个逻辑点有问题，应该只取到当天的价格-而且只有绘制红线的最用，可以考虑大量复盘不做统计可视化的时候屏蔽掉这个逻辑
                # price = getDateFromMarket_New(all_price_data)
                # 量化模拟进出场计算
                quantization(shareid,price_flag,all_price_data,startTime,startIndex,endIndex)
                for punit in pricedata.iterrows():
                    punit_map = {}
                    punit_map["date"] = punit[0]
                    punit_map["open"] = '%.3f' % punit[1]['open']
                    punit_map["high"] = '%.3f' % punit[1]['high']
                    punit_map["low"] = '%.3f' %  punit[1]['low']
                    punit_map["close"] = '%.3f' % punit[1]['close']
                    punit_map["vol"] = '%.3f' % punit[1]['volume']
                    unit_price_list.append(punit_map)

                    red_unit_map = {}
                    red_unit_map["date"] = punit[0]
                    red_val_list.append(red_unit_map)

                unitMap["data"] = unit_price_list
                unitMap["red"] = red_val_list
                jsondata = json.dumps(unitMap)

                if os.path.exists("data/glue-data/" +shareid) == False:
                    os.mkdir("data/glue-data/" +shareid)
                with open("data/glue-data/" + shareid +"/" + str(val[0]) + ".json" + "", "w+") as rf:
                    rf.write(jsondata)
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
        for id in f.xreadlines():
            ids = id.strip()
            shaidIdList.append(ids)

    dict = {}

    map = {}
    result_list = []

    start = time.clock()
    count = 0
    # l = dict.values()
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

#     最后生成索引目录

    for i in os.listdir('data/glue-data/'):
        index_map = {}
        if os.path.isdir('data/glue-data/' + i):
            f_list = []
            for fs in os.listdir('data/glue-data/'+i):
                if os.path.isfile('data/glue-data/' + i+"/"+fs):
                    f_list.append(fs)
        index_map[i] = f_list

    with open('data/key.json', 'w') as f:
        json.dump(index_map, f)
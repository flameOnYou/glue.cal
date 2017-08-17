# -*- coding: utf-8 -*-

"""
量化计算工具类
@author: songy
"""


import datetime
import pandas as pd
"""
比较两个日期字符串之间相差的天数
"""
def date_gap(daystr1,daystr2):
    d1 = datetime.datetime.strptime(daystr1, '%Y-%m-%d')
    d2 = datetime.datetime.strptime(daystr2, '%Y-%m-%d')
    return (d1-d2).days

'''
给出N日前的字符串，遇到周末则往前取一天
n 前几天
madeTime,类型datetime，指定时间
'''

def get_nday_before(data_str,n):
    # print "====",data_str,n
    madeTime = datetime.datetime.strptime(data_str, '%Y-%m-%d')
    date = madeTime + datetime.timedelta(days=-n)
    #    周末
    week = date.isoweekday()
    if week == 6 or week == 7:
        return get_nday_before(date.strftime('%Y-%m-%d'),1)
    return date.strftime('%Y-%m-%d')

"""
获取今日字符串
"""

def get_today_str():
    return datetime.datetime.now().strftime('%Y-%m-%d')


"""
x的数据格式为
日期从小到大排列
l = {"2010-07-01" : "35.12"}
"""


class Unit:

    def __init__(self,date,price):
        self.date = date
        self.price = price
    
    @staticmethod
    def compare(unita,unitb):
        return date_gap(unita.date,unitb.date)

l = [35.12,31.61,34.10,31.12,32.16]


"""
计算SMA函数
往回倒退五天开始计算
例如SMA(C,5,1)
求X的N日移动平均，M为权重
第一天收盘价：C1=35.12;
第二天收盘价：C2=31.61;
第三天收盘价：C3=34.10;
第四天收盘价：C4=31.12;
第五天收盘价：C5=32.16;

第一天数值：S1=C1=35.120;
第二天数值：S2=[M*C2+(N-M)*S1]/N=(1×31.61+4×35.120)÷5=34.418
第三天数值：S3=[M*C3+(N-M)*S2]/N=(1×34.10+4×34.418)÷5=34.354
第四天数值：S4=[M*C4+(N-M)*S3]/N=(1×31.12+4×34.354)÷5=33.708
第五天数值：S5=[M*C5+(N-M)*S4]/N=(1×32.16+4×33.708)÷5=33.398

函数传参说明
x必须是Unit的列表[Unit1,Unit2.....]
eg,计算2016-01-05的sma值
1.取出日期列表和对应的价格值
"2016-01-01"
"2016-01-02"
"2016-01-04"
"2016-01-03"
"2016-01-05"

2.然后组合成 [Unit1,Unit2...]

3.然后丢如函数sma()
"""
def sma_calculate(unit_list,n,m):
    s = unit_list[0].price
    for i in range(1,n):
        s = (m * unit_list[i].price + (n-m)*s )/n
        # print '%.3f' % s
    return s

"""
使用示例
# 读入所有数据
coreId = "600005"
filename = "data/price-data/"+coreId +".csv"
df = pd.read_csv(filename,encoding="gbk",index_col =0,skiprows =1,names=["datetime","coreId","name","close","high","low","open","前收盘","涨跌额","涨跌幅","换手率","volume","成交金额","总市值","流通市值","成交笔数"])

sma(df,"2017-01-06",5,1)

"""


def sma(datafreams,datestr, n,m):
    dt = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    if dt.isoweekday() == 6 or dt.isoweekday() == 7:
        print "今日是周末,求出的值是周五的sma值"
    date_list = []
    i = 0

    index_list = list(datafreams.index)
    unit_list = []
    for i in range(0,n):
        index = index_list.index(datestr) - i
        if index <= 0:
#             返回0说明异常值,此处为没有足够多的日期来运算
            return 0
#         高耗性能代码
        dt = datafreams.ix[index].name
#         高耗性能代码
        p = ( datafreams.ix[index].high + datafreams.ix[index].low )/2
        unit = Unit(dt,p)
        unit_list.append(unit)        
    return sma_calculate(unit_list,n,m)


"""
获取某日的价格最高价/1000作为比较的基础价格
"""
def orderBase(df,datestr):
    if datestr in list(df.index):
        return df.ix[datestr].high / 1000 + 0.01
    else:
        # 取前一天
        d = get_nday_before(datestr,1)
        return orderBase(df,d)

"""
判断一个日期字符串是否是周末
"""
def isweekday(datestr):
    dt = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    if dt.isoweekday() == 6 or dt.isoweekday() == 7:
        return True
    return False

"""
dataframe倒序
"""
def dfreserve(df):
    df = df.iloc[::-1]
    return df

if __name__ == '__main__':
    coreId = "600051"
    filename = "data/price-data/"+coreId +".csv"
    df = pd.read_csv(filename,encoding="gbk",index_col =0,skiprows =1,names=["datetime","coreId","name","close","high","low","open","前收盘","涨跌额","涨跌幅","换手率","volume","成交金额","总市值","流通市值","成交笔数"])
    print orderBase(df,"2017-05-29")
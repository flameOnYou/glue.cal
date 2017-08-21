# -*- coding: utf-8 -*-

import pandas as pd

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
	filename = coreId +".csv"
	df = pd.read_csv(filename,encoding="gbk",index_col =0,skiprows =1,names=["datetime","coreId","name","close","high","low","open","前收盘","涨跌额","涨跌幅","换手率","成交量","成交金额","总市值","流通市值","成交笔数"])
	del df['coreId']
	del df['name']
	return df

if __name__ == '__main__':
	df = read_hit_csv('600051')
	print df.index
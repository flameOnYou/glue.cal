# -*- coding: utf-8 -*-
"""
分析report.csv文件
"""
import pandas as pd

"""
年份列表
['2009', '2008', '2007', '2015', '2014', '2017', '2016', '2011', '2010', '2013', '2012']
"""
df = pd.read_csv("data/report.csv")
year_list = []
win_year_list = []
for i in df.iterrows():
	# 最后一个表示利润
	# print len(i[1])
	profile = i[1][len(i[1]) - 1] 
	if profile < 0:
		dataStr = i[1][1]
		# print dataStr[0:4]。
		year_list.append(dataStr[0:4])
	if profile > 0:
		dataStr = i[1][1]
		# print dataStr[0:4]。
		win_year_list.append(dataStr[0:4])
# print len(year_list)
a = {}
for i in year_list:
	if year_list.count(i)>1:
		a[i] = year_list.count(i)

b = {}
for i in win_year_list:
	if win_year_list.count(i)>1:
		b[i] = win_year_list.count(i)
# reverse=True :降序
# lost_list = sorted(a.items(), lambda x, y: cmp(x[1], y[1]),reverse=True)
# win_list =  sorted(b.items(), lambda x, y: cmp(x[1], y[1]),reverse=True)
print list(set(win_year_list))
# print (lost_list)
# print (win_list)

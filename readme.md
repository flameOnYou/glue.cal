### 交易系统说明
    该交易系统由3个简单计算方法构成
-   ####   OrderBase 
```bash
    每个价格每天都存在一个OrderBase 称为价格基础
    该价格基础计算公式为从该只股票要计算的那天的
    前一天的最高价除以1000
```
```math
    OrderBase=  \frac{h_y}{1000}
```  
-   ####    SMA值
```python
计算示例:
例如求[2017-08-08]日的SMA(C,5,1)的值(C表示收盘价)
计算SMA函数
往回倒退五天开始计算
例如SMA(C,5,1)
求X的N日移动平均，M为权重

以下为基本数据，C表示收盘价(中间过滤所有没有价格的日期,例如周末和节假日)
[2017-08-02]：C1=35.12;
[2017-08-03]：C2=31.61;
[2017-08-04]：C3=34.10;
[2017-08-07]：C4=31.12;
[2017-08-08]：C5=32.16;

S1-S5表示SMA值
[2017-08-02]：S1=C1=35.120;
[2017-08-03]：S2=[M*C2+(N-M)*S1]/N=(1×31.61+4×35.120)÷5=34.418
[2017-08-04]：S3=[M*C3+(N-M)*S2]/N=(1×34.10+4×34.418)÷5=34.354
[2017-08-07]：S4=[M*C4+(N-M)*S3]/N=(1×31.12+4×34.354)÷5=33.708
[2017-08-08]：S5=[M*C5+(N-M)*S4]/N=(1×32.16+4×33.708)÷5=33.398

最终[2017-08-08]日的SMA(C,5,1) = 33.398


    以下是python程序实现，基础结构使用pandas的dataframe



"""
基础结构单元Unit(价格，日期)
"""
class Unit:

    def __init__(self,date,price):
        self.date = date
        self.price = price
    
    @staticmethod
    def compare(unita,unitb):
        return date_gap(unita.date,unitb.date)
        

"""
@unit_list：Unit对象的集合
"""

def sma_calculate(unit_list,n,m):
    s = unit_list[0].price
    for i in range(1,n):
        s = (m * unit_list[i].price + (n-m)*s )/n
        # print '%.3f' % s
    return s

```
-   ####    移动平均值 moveAverage
```python
和上面两个指标一样,每天一样会有一个移动平均值

这个移动平均值是经过二分法处理过的移动平均值 
处理步骤
1.将每日的最高价+最低价除以2变成每日的基准值记作p
2.将要运算的股票从开盘至今的所有价格都处理一遍形成列表 plist
plist ={('2010-01-02',p1),('2010-01-03',p2),('2010-01-04',p3).....}

具体实例:

    依据集合 plist,求moveAverage("2017-08-08",5,3)的移动平均值

    将2017-08-02 ~ 2017-08-08(取决于第二个参数,共5天 05,04,03,02,01,同样忽略节假日等没有价格的日期)的
    p值相加除以3得出2017-08-08的移动平均值
    
    python代码如下:

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

```
-   ####    交易逻辑(SMA版本)
#### 计算出当日
1.     OrderBase
1.     green = sma(day,3,5)
1.     red = sma(day,5,8)
1.     blue = sma(day,8,13)
 
    如果 abs(red - green) <= orderBase 并且 abs(red - blue) <= orderBase
    则判定当日为一个均线粘合点  
    当连续三个交易日出现均线粘合的时候则判断条件成立准备做单

### 做单规则为:
- 当三个交易日出现均线粘合的时候，可以得出两个价格点Max,和Min,
- Max是这三个交易日的最高价，Min是这三日的最低价，当价格高于最高价的时候选择进场，止损设置在最低价位置,止盈放在当前价格+(Max-Min)的地方。
- 这个时候有两种情况，第一种是直接止损，这个时候就算出场了，统计亏损
- 第二种情况是止盈了，这个时候平半仓,然后用sma值止损，当价格波动到sma值的时候平仓出场
- 当完成了以上步骤之后才可以继续找下一个粘合点
python代码为quantization



    
-   ####    交易逻辑(moveAverage版本)
将上述sma计算的地方换成moveAverage
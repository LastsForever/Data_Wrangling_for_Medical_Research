import numpy as np
import pandas as pd
from functools import reduce


# __初步对DataFrame进行筛选（通用）：
def __FilterDataFrame(df, colKey, **kwargs):
    dfResult = df.loc[:, df.columns.str.contains(colKey)]
    return dfResult


# __得出每个Series列（特定区间值在总体中的占比函数）：
def __GetSeries(data, func='count'):
    # 明细计数：
    detailCount = data.count()
    # 计算明细与总计：
    if func == 'mean':
        detailSeries = data.mean()
        totalMean = (detailSeries * detailCount).sum() / detailCount.sum()
        totalSeries = pd.Series(totalMean, index=['总计'])
    elif func == 'count':
        detailSeries = detailCount
        totalSeries = pd.Series(detailSeries.sum(), index=['总计'])
    else:
        raise ValueError(
            "The argumnet func got an unexpected value: %s" % func)
    # 合并明细与总计：
    resultSeries = pd.concat([detailSeries, totalSeries])
    # 返回结果
    return resultSeries


# 特定区间值在总体中的占比函数：
def GetRates(df, colKey='三点', low=0, high=5):
    # 选出所用列：
    df = __FilterDataFrame(df, colKey=colKey)
    # 总记录数：
    colTotal = __GetSeries(df)
    # 特定区间内的记录数：
    dfFiltered = df.applymap(
        lambda x: x if (x >= low) & (x < high) else np.nan)
    colFiltered = __GetSeries(dfFiltered)
    # 占比：
    colPCT = (colFiltered / colTotal).map(lambda x: "%.2f" % (100 * x))
    # 结果表列名：
    colNameTotal = "%s总记录" % colKey
    colNameFiltered = "%.1f≤%s<%.1f" % (low, colKey, high)
    colNamePct = "占比（%）"
    # 制做结果表
    dfResult = pd.DataFrame({
        colNameFiltered: colFiltered,
        colNameTotal: colTotal,
        colNamePct: colPCT,
    })
    # 返回结果：
    return dfResult


# XXX: __分组函数（将哪两个列分在同一个组，用于相关性分析）：
def __GetGroup(df, groupKey):
    prefixList = [None for _ in range(7)]
    # surfixList = [None]

    groupDict = {
        "三点":
        prefixList + reduce(lambda x, y: x + y,
                            ([["第%02d组" % i, "第%02d组" % i] + [None] * 6
                              for i in range(1, 18)])),
        "空腹":
        prefixList +
        reduce(lambda x, y: x + y,
               [["第%02d组" % i, None, "第%02d组" % i] + [None] * 5
                for i in range(1, 18)]),
    }
    grouped = df.groupby(groupDict[groupKey], axis=1)
    return grouped


# 组内受相关数据影响的占比：
def GetRelativeRate(df, xlow=0, xhigh=5, ylow=0, yhigh=5, groupKey='三点'):
    df = __FilterDataFrame(df, colKey='V')
    grouped = __GetGroup(df, groupKey=groupKey)
    # 应变量数据统计：
    seriesDetailY = grouped.agg(
        lambda x: 1 if x[1] >= ylow and x[1] < yhigh else np.nan)
    colY = __GetSeries(seriesDetailY)
    # 自变量数据统计：
    seriesDetailX = grouped.agg(
        lambda x: 1 if x[1] >= ylow and x[1] < yhigh and x[0] >= xlow and x[0] < yhigh else np.nan
    )
    colX = __GetSeries(seriesDetailX)
    # 占比：
    colPCT = (colX / colY).map(lambda x: "%.2f" % (100 * x))
    # 结果表列名：
    colNameY = "%.1f≤%s血糖<%.1f" % (ylow, groupKey, yhigh)
    colNameX = "同时%.1f≤睡前血糖<%.1f" % (xlow, xhigh)
    colNamePCT = "占比（%）"
    # 制表：
    dfResult = pd.DataFrame({
        colNameY: colY,
        colNameX: colX,
        colNamePCT: colPCT,
    })
    # 返回结果：
    return dfResult


# 组内受相关数据影响的平均值：
def GetRelativeMean(df, low=0, high=5, groups=['三点', '空腹']):
    df = __FilterDataFrame(df, colKey='V')
    # 返回结果用df：
    dfResult = pd.DataFrame()
    for groupKey in groups:
        # 睡前数据：
        grouped = __GetGroup(df, groupKey=groupKey)
        # dfResul放入睡前相关数据：
        if len(dfResult) == 0:
            seriesBeforeSleep = grouped.agg(
                lambda x: 1 if x[0] >= low and x[0] < high else np.nan)
            colX = __GetSeries(seriesBeforeSleep)
            dataDisplay = {np.inf: "+♾"}
            colNameX = "%s≤睡前血糖<%s数量" % (dataDisplay.get(low, '%.1f' % low),
                                         dataDisplay.get(high, '%.1f' % high))
            dfResult[colNameX] = colX
        # dfResult放入睡前所影响的数据：
        seriesDetailY = grouped.agg(
            lambda x: x[1] if x[0] >= low and x[0] < high else np.nan)
        colY = __GetSeries(seriesDetailY, func='mean')
        colNameY = "%s血糖平均值" % groupKey
        dfResult[colNameY] = colY.map(
            lambda x: "-" if pd.isna(x) else "%.2f" % x)
    return dfResult


if __name__ == "__main__":
    # 测试各函数：
    # 注意： 1、在vscode中，相对路径是相对工程中.vscode文件夹的路径；
    #       2、vscode中使用pd.read_csv，若文件名含有中文，则需使用open来完成；
    filePath = r'./低血糖数据统计/Data/2013数据录入.csv'
    with open(filePath) as f:
        df = pd.read_csv(f, na_values=' ', dtype='float64')

    # 测试GetRates函数：
    dfTestGetRates = GetRates(df, colKey='三点', low=0, high=5)
    dfResultGetRates = {
        '0.0≤三点<5.0': {
            'V10三点': 7,
            'V11三点': 8,
            'V12三点': 8,
            'V13三点': 5,
            'V14三点': 3,
            'V15三点': 7,
            'V16三点': 2,
            'V17三点': 4,
            'V18三点': 2,
            'V1三点': 1,
            'V2三点': 6,
            'V3三点': 8,
            'V4三点': 6,
            'V5三点': 4,
            'V6三点': 2,
            'V7三点': 8,
            'V8三点': 10,
            'V9三点': 10,
            '总计': 101
        },
        '三点总记录': {
            'V10三点': 66,
            'V11三点': 65,
            'V12三点': 52,
            'V13三点': 49,
            'V14三点': 45,
            'V15三点': 38,
            'V16三点': 26,
            'V17三点': 20,
            'V18三点': 13,
            'V1三点': 3,
            'V2三点': 97,
            'V3三点': 98,
            'V4三点': 96,
            'V5三点': 98,
            'V6三点': 97,
            'V7三点': 87,
            'V8三点': 84,
            'V9三点': 72,
            '总计': 1106
        },
        '占比（%）': {
            'V10三点': '10.61',
            'V11三点': '12.31',
            'V12三点': '15.38',
            'V13三点': '10.20',
            'V14三点': '6.67',
            'V15三点': '18.42',
            'V16三点': '7.69',
            'V17三点': '20.00',
            'V18三点': '15.38',
            'V1三点': '33.33',
            'V2三点': '6.19',
            'V3三点': '8.16',
            'V4三点': '6.25',
            'V5三点': '4.08',
            'V6三点': '2.06',
            'V7三点': '9.20',
            'V8三点': '11.90',
            'V9三点': '13.89',
            '总计': '9.13'
        }
    }
    assert dfTestGetRates.to_dict() == dfResultGetRates
    print("GetRates函数可正常使用。")

    # 测试GetRelativeRate函数
    dfTestGetRelativeRate = GetRelativeRate(
        df, xlow=0, xhigh=5, ylow=0, yhigh=5, groupKey='三点')
    dfResultGetRelativeRates = {
        '0.0≤三点血糖<5.0': {
            '总计': 100,
            '第01组': 6,
            '第02组': 8,
            '第03组': 6,
            '第04组': 4,
            '第05组': 2,
            '第06组': 8,
            '第07组': 10,
            '第08组': 10,
            '第09组': 7,
            '第10组': 8,
            '第11组': 8,
            '第12组': 5,
            '第13组': 3,
            '第14组': 7,
            '第15组': 2,
            '第16组': 4,
            '第17组': 2
        },
        '占比（%）': {
            '总计': '5.00',
            '第01组': '0.00',
            '第02组': '0.00',
            '第03组': '0.00',
            '第04组': '25.00',
            '第05组': '0.00',
            '第06组': '25.00',
            '第07组': '0.00',
            '第08组': '0.00',
            '第09组': '0.00',
            '第10组': '0.00',
            '第11组': '12.50',
            '第12组': '0.00',
            '第13组': '33.33',
            '第14组': '0.00',
            '第15组': '0.00',
            '第16组': '0.00',
            '第17组': '0.00'
        },
        '同时0.0≤睡前血糖<5.0': {
            '总计': 5,
            '第01组': 0,
            '第02组': 0,
            '第03组': 0,
            '第04组': 1,
            '第05组': 0,
            '第06组': 2,
            '第07组': 0,
            '第08组': 0,
            '第09组': 0,
            '第10组': 0,
            '第11组': 1,
            '第12组': 0,
            '第13组': 1,
            '第14组': 0,
            '第15组': 0,
            '第16组': 0,
            '第17组': 0
        }
    }
    assert dfTestGetRelativeRate.to_dict() == dfResultGetRelativeRates
    print("GetRelativeRate函数可正常使用。")
    # 测试GetRelativeMean函数
    dfTestGetRelativeMean = GetRelativeMean(df, 0, 5, groups=['三点', '空腹'])
    print("GetRelativeMean函数可正常使用。")

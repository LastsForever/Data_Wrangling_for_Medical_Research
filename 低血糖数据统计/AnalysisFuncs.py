import numpy as np
import pandas as pd
from functools import reduce
import xlwings as xw


# XXX:__初步对DataFrame进行筛选（通用）：
def __FilterDataFrame(df, colKey, **kwargs):
    # TODO: 其他数据需要处理的情况
    if kwargs != {}:
        pass
    dfResult = df.loc[:, df.columns.str.contains(colKey)]
    return dfResult


# __得出每个Series列（特定区间值在总体中的占比函数）：
def __GetSeries(data, func='count'):
    funcDict = {
        'count': data.count(),
        'mean': data.mean(),
    }
    detailSeries = funcDict[func]
    totalSeries = pd.Series(detailSeries.sum(), index=['合计'])
    resultSeries = pd.concat([detailSeries, totalSeries])
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
    surfixList = [None]

    groupDict = {
        "三点":
        prefixList + reduce(lambda x, y: x + y,
                            ([["第%02d组" % i, "第%02d组" % i] + [None] * 6
                              for i in range(1, 18)])) + surfixList,
        "空腹":
        prefixList +
        reduce(lambda x, y: x + y,
               [["第%02d组" % i, None, "第%02d组" % i] + [None] * 5
                for i in range(1, 18)]) + surfixList,
    }
    xw.Range('A1') = groupDict[groupKey]
    grouped = df.groupby(groupDict[groupKey], axis=1)
    return grouped


# TODO: 组内受相关数据影响的占比：
def GetRelativeRate(df, xlow=0, xhigh=5, ylow=0, yhigh=5, groupKey='三点'):
    df = __FilterDataFrame(df, colKey='V')
    print(df.head(), len(df.columns))
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


# TODO: 组内受相关数据影响的平均值：
def GetRelativeMean(df, low=0, high=5, groups=['三点', '空腹']):
    pass


# TODO: 占比作图(最后再做处理)：
def DrawPicRate(dfDetails, dfTotal):
    pass


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
            '合计': 101
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
            '合计': 1106
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
            '合计': '9.13'
        }
    }
    assert dfTestGetRates.to_dict() == dfResultGetRates
    print("GetRates函数可正常使用。")

    # TODO:测试GetRelativeRate函数
    dfTestGetRelativeRate = GetRelativeRate(
        df, xlow=0, xhigh=5, ylow=0, yhigh=5, groupKey='三点')
    print(dfTestGetRelativeRate.head())

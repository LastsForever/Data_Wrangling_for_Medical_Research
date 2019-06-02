#%%
# 前期准备：
from numpy import inf
from pandas import read_csv
from AnalysisFuncs import *
from platform import system
from IPython.display import display
from IPython.display import HTML
from IPython.core import display as di
get_ipython().run_line_magic('matplotlib', 'inline')

# 1、基础设置：
# （1）设置作图尺寸大小：
plt.rcParams['figure.dpi'] = 100
# （2）设置导出HTML时是否隐藏代码：
hide_code = True  # 设置是否隐藏代码。
if hide_code:
    di.display_html(
        '<script>jQuery(function() {if (jQuery("body.notebook_app").length == 0) { jQuery(".input_area").toggle(); jQuery(".prompt").toggle();}});</script>',
        raw=True)
    CSS = """#notebook div.output_subarea {max-width:100%;}"""  #changes output_subarea width to 100% (from 100% - 14ex)
    HTML('<style>{}</style>'.format(CSS))

# 2、问题解决：
# （1）解决matplotlib作图时中文乱码问题：
sysName = system()
if sysName == 'Windows':
    plt.rcParams['font.sans-serif'] = ['SimHei']  #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  #用来正常显示负号
elif sysName == 'Darwin':
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False  #解决保存图像是负号'-'显示为方块的问题

# 数据读入：
filePath = r'2013数据录入.csv'
df = read_csv(filePath, na_values=' ', dtype='float64')

#%% [markdown]
# ## 一、单一变量数据统计：
#%% [markdown]
# ### （一）所有三点血糖低于5的数量和占比：

#%%
df3AM0to5, dfPlot3AM0to5 = GetRates(df, keywords='三点', low=0, high=5)
df3AM0to5

#%%
# 作图：
DrawPicRate(dfPlot3AM0to5)

#%% [markdown]
# ### （二）所有睡前血糖低于5的数量和占比：

#%%
dfBeforeSleep0to5, dfPlotBeforeSleep0to5 = GetRates(
    df, keywords='睡前', low=0, high=5)
dfBeforeSleep0to5

#%%
DrawPicRate(dfPlotBeforeSleep0to5)

#%% [markdown]
# ### （三）所有睡前血糖在5到7之间的数量和占比：

#%%
dfBeforeSleep5to7, dfPlotBeforeSleep5to7 = GetRates(
    df, keywords='睡前', low=5, high=7)
dfBeforeSleep5to7

#%%
# 作图
DrawPicRate(dfPlotBeforeSleep5to7)

#%% [markdown]
# ### （四）所有空腹血糖小于5的数量和占比：

#%%
dfBeforeMeal0to5, dfPlotBeforeMeal0to5 = GetRates(
    df, keywords='空腹', low=0, high=5)
dfBeforeMeal0to5

#%%
# 作图
DrawPicRate(dfPlotBeforeMeal0to5)

#%% [markdown]
# ## 二、分组对比研究：
#%% [markdown]
#   设每晚睡前至次日晚餐后的时间段为一组，共17个组。
#%% [markdown]
# ### (一) 睡前血糖介于[0.0, 5.0)对三点血糖的影响数据：

#%%
dfRelative3AM, _ = GetRelativeRate(
    df, xlow=0, xhigh=5, ylow=0, yhigh=5, group='三点')
dfRelative3AM

#%% [markdown]
# ### (二) 睡前血糖介于[5.0, 7.0)对空腹值介于[0.0, 7.0)的影响

#%%
dfRelativeBeforeMeal, _ = GetRelativeRate(
    df, xlow=5, xhigh=7, ylow=0, yhigh=7, group='空腹')
dfRelativeBeforeMeal

#%% [markdown]
# ### (三)睡前血糖小于5时，三点和空腹血糖的平均值

#%%
GetRelativeMean(df, 0, 5, groups=['三点', '空腹'])

#%% [markdown]
# ### (四)睡前血糖介于[5.0, 7.0)时，三点和空腹血糖的平均值

#%%
GetRelativeMean(df, 5, 7, groups=['三点', '空腹'])

#%% [markdown]
# ### (五)睡前血糖大于7.0时，三点和空腹血糖的平均值

#%%
GetRelativeMean(df, 7, inf, groups=['三点', '空腹'])

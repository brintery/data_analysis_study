# Copyright (c) 2018 Mindon
#
# -*- coding:utf-8 -*-
# @Script: dataanalysis.py
# @Author: Mindon
# @Email: gaomindong@live.com
# @Create At: 2018-08-30 18:10:34
# @Last Modified By: Mindon
# @Last Modified At: 2018-09-05 17:58:57
# @Description: This is description.

import pandas as pd
import numpy as np

# read data
data = pd.read_csv('DataAnalyst.csv', encoding='gb2312')
data.info()
data.head()


# process data
# duplicate data
len(data['positionId'].unique())
dup_data = data.drop_duplicates(subset='positionId', keep='first')
len(dup_data)

def cut_word(word, method):
    # extract salary
    position = word.find('-')
    length = len(word)

    if position != -1:
        bottom_salary = word[:position-1]
        top_salary = word[position+1:length-1]
    else:
        bottom_salary = word[:word.upper().find('K')]
        top_salary = bottom_salary

    if method == 'bottom':
        return bottom_salary
    else:
        return top_salary


dup_data['bottom_salary'] = dup_data['salary'].apply(cut_word, method='bottom')
dup_data['top_salary'] = dup_data['salary'].apply(cut_word, method='top')
dup_data.head()
dup_data.info()


# caculate average salary
dup_data['bottom_salary'] = dup_data['bottom_salary'].astype('int')
dup_data['top_salary'] = dup_data['top_salary'].astype('int')
dup_data['avg_salary'] = dup_data.apply(
    lambda x: (x['bottom_salary']+x['top_salary'])/2, axis=1)


# use data to anlaysis
aly_data = dup_data[['city', 'companyShortName', 'companySize',
                     'education', 'positionName', 'positionLables',
                     'workYear', 'avg_salary']]
aly_data.head()


# count the number and salary of work
aly_data['city'].value_counts().plot(kind='bar')
aly_data.describe()
aly_data.groupby('city').describe()
aly_data['avg_salary'].plot(kind='box')
aly_data['avg_salary'].plot(kind='hist')
aly_data.boxplot(column='avg_salary', by='city')
aly_data.boxplot(column='avg_salary', by='education')
data_shbj = aly_data[aly_data['city'].isin(['上海', '北京'])]
data_shbj = aly_data[(aly_data['city']=='上海')|(aly_data['city']=='北京')]
data_shbj.tail()
data_shbj.boxplot(column='avg_salary', by=['city', 'education'])


# aggeration statics
aly_data.groupby('city').count()
aly_data['avg_salary'].groupby(aly_data['city']).mean()
aly_data['avg_salary'].groupby(aly_data['city']).describe()
aly_data.groupby(['city', 'education']).mean().unstack().plot(kind='bar')
aly_data['avg_salary'].groupby(
    [aly_data['city'], aly_data['education']]).count().unstack()
aly_data.groupby('companyShortName')['avg_salary'].agg(
    ['count', 'mean']).sort_values(by='count', ascending=False)


# apply statics
# caculate the top 5 company for each city
def topN(df, n=5):
    counts = df.value_counts().sort_values(ascending=False)[:n]
    # counts = df.groupby('companyShortName').count().sort_values(ascending=False)[:n]
    return counts

aly_data.groupby('city')['companyShortName'].apply(topN)


# hist statics
aly_data[aly_data['city']=='上海']['avg_salary'].plot(kind='hist', bins=15, normed=1, color='r')
aly_data[aly_data['city']=='北京']['avg_salary'].plot(kind='hist', bins=15, normed=1, alpha=0.3)


# bucket analysis
bins = [0, 3, 5, 10, 15, 20, 30, 100]
level = ['0-3', '3-5', '5-10', '10-15', '15-20', '20-30', '30+']
aly_data['level'] = pd.cut(aly_data['avg_salary'], bins=bins, labels=level)
aly_data.head()

aly_level = aly_data.groupby(['city', 'level'])['avg_salary'].count().unstack()
aly_level_pct = aly_level.apply(lambda x: x/x.sum(), axis=1)
aly_level.head()
aly_level_pct.head()
aly_level_pct.plot(kind='bar', stacked=True, figsize=(14,6))

# process lables
label_data = aly_data['positionLables'].str[1:-1].str.replace(' ', '')
label_data.head()
df_label_data = label_data.dropna().str.split(',').apply(pd.value_counts)
df_label_data.unstack().head()
df_label_data.stack().head()
df_label_data.unstack().dropna().reset_index().groupby('level_0').count()
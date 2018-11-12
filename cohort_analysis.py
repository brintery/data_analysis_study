# Copyright (c) 2018 Your Name
#
# -*- coding:utf-8 -*-
# @Script: cohort_analysis.py
# @Author: Your Name
# @Email: someone@gmail.com
# @Create At: 2018-11-09 14:18:31
# @Last Modified By: Your Name
# @Last Modified At: 2018-11-12 09:12:10
# @Description: This is description.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import os

# %%
# setting
pd.set_option('max_columns', 50)
mpl.rcParams['lines.linewidth'] = 2
sns.set(style='white')

# %%
# read data
df = pd.read_excel('relayfoods.xlsx')
df.head()
df.tail()

# %%
# create order period
df['OrderPeriod'] = df['OrderDate'].apply(lambda x: x.strftime('%Y-%m'))
df.set_index('UserId', inplace=True)

# determine the user's cohort group(based on the first order)
df['CohortGroup'] = df.groupby(level=0)['OrderDate'].min().apply(
    lambda x: x.strftime('%Y-%m'))
df.reset_index(inplace=True)

# roll up data by cohortgroup&orderperiod
grouped = df.groupby(['CohortGroup', 'OrderPeriod'])

cohorts = grouped.agg({'UserId': pd.Series.nunique, 'OrderId': lambda x: x.count(
), 'TotalCharges': lambda x: x.sum()})

cohorts.rename(columns={'UserId': 'TotalUsers',
                        'OrderId': 'TotalOrders'}, inplace=True)

# %%
# label the cohort period for each cohort group
def cohort_period(df):
    """
    Creates a `CohortPeriod` column, which is the Nth period based on the user's first purchase.
    
    Example
    -------
    Say you want to get the 3rd month for every user:
        df.sort(['UserId', 'OrderTime', inplace=True)
        df = df.groupby('UserId').apply(cohort_period)
        df[df.CohortPeriod == 3]
    """
    df['CohortPeriod'] = np.arange(len(df)) + 1
    return df

cohorts = cohorts.groupby(level=0).apply(cohort_period)

# %%
# test which data right
x = df[(df.CohortGroup == '2009-01') & (df.OrderPeriod == '2009-01')]
y = cohorts.ix[('2009-01', '2009-01')]

assert(x['UserId'].nunique() == y['TotalUsers'])
assert(x['TotalCharges'].sum().round(2) == y['TotalCharges'].round(2))
assert(x['OrderId'].nunique() == y['TotalOrders'])

x = df[(df.CohortGroup == '2009-01') & (df.OrderPeriod == '2009-09')]
y = cohorts.ix[('2009-01', '2009-09')]

assert(x['UserId'].nunique() == y['TotalUsers'])
assert(x['TotalCharges'].sum().round(2) == y['TotalCharges'].round(2))
assert(x['OrderId'].nunique() == y['TotalOrders'])

x = df[(df.CohortGroup == '2009-05') & (df.OrderPeriod == '2009-09')]
y = cohorts.ix[('2009-05', '2009-09')]

assert(x['UserId'].nunique() == y['TotalUsers'])
assert(x['TotalCharges'].sum().round(2) == y['TotalCharges'].round(2))
assert(x['OrderId'].nunique() == y['TotalOrders'])

# %%
# user retention by cohort group
# reset index and set index to cohort group and cohort period
cohorts.reset_index(inplace=True)
cohorts.set_index(['CohortGroup', 'CohortPeriod'], inplace=True)

# create a Series holding the total size of each CohortGroup
cohort_group_size = cohorts.groupby(level=0)['TotalUsers'].first()

# caculate retention
cohorts['TotalUsers'].unstack(0).head()
user_retention = cohorts['TotalUsers'].unstack(0).divide(cohort_group_size, axis=1)
user_retention.T

# %%
# plot user retention
user_retention[['2009-06', '2009-07', '2009-08']].plot(kind='line')
plt.title("Cohorts: User Retention")
plt.ylabel("% of Cohort Purchasing")

# plot user retention use seaborn
sns.set(style="whitegrid")
plt.title("Cohorts: User Retention")
plt.figure(figsize=(12, 8))
sns.heatmap(user_retention.T, mask=user_retention.T.isnull(), annot=True, fmt='.0%')

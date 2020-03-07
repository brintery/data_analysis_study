# Copyright (c) 2018 Mindon
#
# -*- coding:utf-8 -*-
# @Script: consumer_analysis.py
# @Author: Mindon
# @Email: gaomindong@live.com
# @Create At: 2018-09-06 10:43:26
# @Last Modified By: Your Name
# @Last Modified At: 2018-10-22 14:29:17
# @Description: This is description.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

#%%
# set the plot style
plt.style.use('ggplot')

# read data
columns = ['user_id', 'order_dt', 'order_products', 'order_amount']
data = pd.read_table('CDNOW_master.txt', names=columns, sep=r'\s+')
data.head()

#%%
# process date
data['order_date'] = pd.to_datetime(data['order_dt'], format='%Y%m%d')
data['month'] = data['order_date'].values.astype('datetime64[M]')

#%%
# fundmental analysis
data.describe()
data.info()

#%%
# analysis by user
user_group = data.groupby('user_id').sum()
user_group.head()
user_group.describe()

#%%
# analysis by date
data.groupby('month')['order_products'].sum().plot()

#%%
# user scatter to find relationship of order_amount and order_products
data.plot(kind='scatter', x='order_amount', y='order_products')
data.groupby('user_id').sum().plot(kind='scatter',
                                   x='order_amount', y='order_products')

#%%
# user hist analysis why order_amount has declined
data['order_amount'].plot(kind='hist')
data.groupby('user_id')['order_amount'].sum().plot(kind='hist')

#%%
# check the user first and last shopping time
data.groupby('user_id')['month'].min().value_counts()
data.groupby('user_id')['month'].max().value_counts()

#%%
# caculate repurchase rate
# pivot analysis
pivot_counts = data.pivot_table(
    index='user_id', columns='month', values='order_dt', aggfunc='count').fillna(0)
pivot_counts.head()
columns_month = data['month'].sort_values().astype('str').unique()
pivot_counts.columns = columns_month
columns_month

pivot_counts_rp = pivot_counts.applymap(
    lambda x: 1 if x > 1 else np.nan if x == 0 else 0)
pivot_counts_rp.head()
(pivot_counts_rp.sum()/pivot_counts_rp.count()).plot(figsize=(10, 4))

#%%
# caculate back purchase rate
# pivot analysis
pivot_amounts = data.pivot_table(
    index='user_id', columns='month', values='order_amount', aggfunc='mean').fillna(0)
columns_month = data['month'].sort_values().astype('str').unique()
pivot_amounts.columns = columns_month
columns_month
pivot_amounts.head()

pivot_purchase = pivot_amounts.applymap(lambda x: 1 if x > 1 else 0)
pivot_purchase.head()

#%%
def purchase_return(data):
    status = []
    for i in range(17):
        if data[i] == 1:
            if data[i+1] == 1:
                status.append(1)
            else:
                status.append(0)
        else:
            status.append(np.nan)
    status.append(np.nan)
    return status

#%%
pivot_purchase_return = pivot_purchase.apply(purchase_return, axis=1)
pivot_purchase_return.head()
(pivot_purchase_return.sum()/pivot_purchase_return.count()).plot()

#%%
# classify users
def classify_users(data):
    status = []

    for i in range(18):
        # is this month have purchase?
        # isn't
        if data[i] == 0:
            # is first don't have purchase?
            # isn't
            if len(status) > 0:
                # is last month have purchase?
                # don't have purchase
                if status[i-1] == 'unreg':
                    status.append('unreg')
                # have purchase
                else:
                    status.append('unactive')
            # is the first
            else:
                status.append('unreg')

        # have purchase
        else:
            # is first have purchase?
            # isn't
            if len(status) > 0:
                # is the last month status?
                # last month is unreg, this is new
                if status[i-1] == 'unreg':
                    status.append('new')
                # last month is unactive, this is return
                elif status[i-1] == 'unactive':
                    status.append('return')
                # last month is active, this is active
                else:
                    status.append('active')
            # first have purchase
            else:
                status.append('new')

    return status

#%%
# classify users, the two method is the same
pivot_purchase_status = pivot_purchase.apply(lambda x: classify_users(x), axis=1)
pivot_purchase_status.head()
test = pivot_purchase.apply(classify_users, axis=1)
test.head()

#%%
# static the number of each user types
purchase_status_counts = pivot_purchase_status.replace('unreg', np.nan).apply(pd.value_counts)
purchase_status_counts.head()
purchase_status_counts.T.plot(kind='area', figsize=(12, 6))

#%%
# caculate return rate
return_rate = purchase_status_counts.apply(lambda x: x/x.sum(), axis=1)
return_rate.head()
return_rate.loc['return'].plot()
return_rate.loc['active'].plot()

#%%
# analysis user quanlity
user_amount = data.groupby('user_id')['order_amount'].sum().sort_values().reset_index()
user_amount['amount_cumsum'] = user_amount['order_amount'].cumsum()
user_amount.tail()
amount_total = user_amount['amount_cumsum'].max()
user_amount['prop'] = user_amount.apply(lambda x: x['amount_cumsum']/amount_total, axis=1)
user_amount['prop'].plot()

#%%
# analysis the able of shopping
user_counts = data.groupby('user_id')['order_dt'].count().sort_values().reset_index()
user_counts.tail()
user_counts['count_cumsum'] = user_counts['order_dt'].cumsum()
counts_total = user_counts['count_cumsum'].max()
user_counts['prop'] = user_counts.apply(lambda x: x['count_cumsum']/counts_total, axis=1)
user_counts['prop'].plot()

#%%
# caculate user life time
user_purchase = data[['user_id', 'order_products', 'order_amount', 'order_date']]
user_purchase.head()
order_date_min = user_purchase.groupby('user_id')['order_date'].min()
order_date_max = user_purchase.groupby('user_id')['order_date'].max()

life_time = (order_date_max-order_date_min).reset_index()
life_time.head()

life_time['life_time'] = life_time['order_date']/np.timedelta64(1, 'D')
life_time[life_time['life_time']>0]['life_time'].plot(kind='hist', bins=100, figsize=(12, 6))
life_time[life_time['life_time']>0]['life_time'].describe()

#%%
# caculate retention rate
user_purchase_retention = pd.merge(left=user_purchase, right=order_date_min.reset_index(), how='inner', on='user_id', suffixes=('', '_min'))
user_purchase_retention.head(50)
user_purchase_retention['order_date_diff'] = user_purchase_retention['order_date'] - user_purchase_retention['order_date_min']

user_purchase_retention['date_diff'] = user_purchase_retention['order_date_diff'].apply(lambda x: x/np.timedelta64(1, 'D'))

bin = [0,3,7,15,30,60,90,180,365]
user_purchase_retention['date_diff'] = user_purchase_retention['date_diff'].astype(int)
user_purchase_retention['date_diff_bin'] = pd.cut(user_purchase_retention['date_diff'], bins=bin)

pivot_retention = user_purchase_retention.pivot_table(index='user_id', columns='date_diff_bin', values='order_amount', aggfunc=sum)
pivot_retention.head()
pivot_retention.mean()

pivot_retention_trans = pivot_retention.fillna(0).applymap(lambda x: 1 if x>0 else 0)
pivot_retention_trans.head()
(pivot_retention_trans.sum()/pivot_retention_trans.count()).plot(kind='bar')

#%%
# caculate the distance of user consume
def diff(data):
    return data['date_diff'] - data['date_diff'].shift(-1)

last_diff = user_purchase_retention.groupby('user_id').apply(diff)
last_diff.head(20)
last_diff.mean()
last_diff.plot(kind='hist')
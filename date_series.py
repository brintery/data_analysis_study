# Copyright (c) 2018 Mindon
#
# -*- coding:utf-8 -*-
# @Script: date_series.py
# @Author: Mindon
# @Email: gaomindong@live.com
# @Create At: 2018-03-26 14:33:10
# @Last Modified By: Mindon
# @Last Modified At: 2018-05-03 10:25:34
# @Description: date_series.

from datetime import datetime
import pandas as pd
import numpy as np


# create date series
dates = [datetime(2018, 3, 1), datetime(2018, 3, 3), datetime(2018, 3, 5),
        datetime(2018, 3, 7), datetime(2018, 3, 9), datetime(2018, 3, 11)]

ts = pd.Series(np.random.randn(6), index=dates)

longer_ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))

long_dates = pd.date_range('1/1/2000', periods=100, freq='W-WED')
long_df = pd.DataFrame(np.random.randn(100, 4), index=long_dates, columns=['Colorado', 'Texas', 'New York', 'Ohio'])

print(ts)
print(longer_ts)
print(long_df)

# index, select and sub-collection
ts['20180307']
ts['07/03/2018']
longer_ts['2001']
print(ts['20180301':'20180305'])
long_df['5-2001']

# date range, frequency, shift
# date range
index = pd.date_range('20110102', '20110201')
index1 = pd.date_range(start='20180302', periods=20, freq='BM', normalize=True)

# freqency
# index2 = pd.date_range(start='20180302', periods=20, freq='1h30min')
index2 = pd.date_range(start='20180302', periods=20, freq='1h30min')
index3 = pd.date_range(start='20180302', periods=20, freq='1h30min')

# shift
ts.shift(2, freq='D')


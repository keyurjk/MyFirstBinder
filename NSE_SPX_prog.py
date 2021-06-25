import pandas as pd
import pandas_datareader as pdr
import pyfolio as pf
import numpy as np
# Import matplotlib
import matplotlib.pyplot as plt
%matplotlib inline
'''
SPX overnight return to determine NSE movement today
SPX 1st-date, NSE 2nd-date. (1st row, 2nd row)
'''
# Get the data for Nasdaq Composite
spx_data = pdr.get_data_yahoo('^IXIC', '2010-1-1', '2021-6-23')
spx_data.head(2)

# get NSE data
nse_data = pdr.get_data_yahoo('^NSEI', '2010-1-1', '2021-6-23')

# Print last 2 rows of the data
nse_data.head(2)

#calculate SPX overnight returns
spx_data['today_returns'] = ((spx_data['Close'].shift(1)-spx_data['Close'])/spx_data['Close'].shift(1))
spx_data.head(5)

#calculate NSE pivots
#Pivot = YD High + Low + Close /3, R1 = (2*Pivot)-Low, S1= (2*Pivot)-High, R2 = Pivot+(H-L) , S2=P-(H-L)
'''
nse_data['pivot'] = (nse_data['High'].shift(1)+nse_data['Low'].shift(1)+nse_data['Close'].shift(1))/3
nse_data['R1'] = (2*nse_data['pivot'])-nse_data['Low'].shift(1)
nse_data['S1'] = (2*nse_data['pivot'])-nse_data['High'].shift(1)
nse_data['R2'] = nse_data['pivot']+(nse_data['High'].shift(1)-nse_data['Low'].shift(1))
nse_data['S2'] = nse_data['pivot']-(nse_data['High'].shift(1)-nse_data['Low'].shift(1))

nse_data.head(5)
'''

# compare SPX return and generate NSE signal
nse_data['SPX_YD_ret'] = spx_data['today_returns'].shift(1)
'''
Strategy: If SPX YD ret is > 0.5%, go long on open PP and book profit if High > 0.5% or exit at close with loss, no strict SL.
Go short, SPX YD ret is < -0.5% on open PP and book profit if High > 0.5% or exit at close with loss, no strict SL.
'''
# Define your conditions on which you want to trade
cond_1 = nse_data.SPX_YD_ret > 0.005
cond_2 = nse_data.SPX_YD_ret < -0.005

# Store it in the signal columns of dataframe data
nse_data['signal'] = np.where(cond_1, 1, 0)
#no_signal = data.signal == 0
nse_data['signal2'] = np.where(cond_2, 2, 0)

nse_data.loc[nse_data.signal2==2].head()
#-------------
nse_data.loc[nse_data.signal==1].describe()

# long returns High - Open
nse_data['intraday_long_returns'] = ((nse_data.loc[nse_data.signal==1].High-nse_data.loc[nse_data.signal==1].Open)/nse_data.loc[nse_data.signal==1].Open)
nse_data['intraday_long_loss'] = ((nse_data.loc[nse_data.signal==1].Close-nse_data.loc[nse_data.signal==1].Open)/nse_data.loc[nse_data.signal==1].Open)

# Short retruns Low -Open (-ve to compare with SPX)
nse_data['intraday_short_returns'] = ((nse_data.loc[nse_data.signal2==2].Low-nse_data.loc[nse_data.signal2==2].Open)/nse_data.loc[nse_data.signal2==2].Open)
nse_data['intraday_short_loss'] = ((nse_data.loc[nse_data.signal2==2].Open-nse_data.loc[nse_data.signal2==2].Close)/nse_data.loc[nse_data.signal2==2].Open)

#long strategy return
ret_cond1 = nse_data.intraday_long_returns >= nse_data.SPX_YD_ret
nse_data['long_ret'] = np.where(ret_cond1, nse_data.intraday_long_returns, nse_data.intraday_long_loss)

ret_cond2 = nse_data.intraday_short_returns <= nse_data.SPX_YD_ret
nse_data['short_ret'] = np.where(ret_cond2, nse_data.intraday_short_returns*-1, nse_data.intraday_short_loss)

#?? TODO pivot analysis on profitable/loss trades.

# long
#strategy_returns = nse_data.loc[nse_data.signal==1].long_ret
#short
strategy_returns = nse_data.loc[nse_data.signal2==2].short_ret

#both
#strategy_returns = nse_data.loc[nse_data.signal==1].long_ret + nse_data.loc[nse_data.signal2==2].short_ret

# plot the returns
(strategy_returns+1).cumprod().plot(figsize=(10, 7), grid=True)
plt.xlabel('Year')
plt.ylabel('Cumulative Strategy Returns')
plt.show()

#plot stats
pf.create_simple_tear_sheet(strategy_returns)

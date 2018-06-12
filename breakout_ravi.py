lag_val = 1
MA_val = 20

entry_thresh = 0.05
exit_thresh = 0.5

rolling_window = 8

portfolio_size = 15
portfolio_allocation = 100
# mypath='F:/Work/Data/ALLDATA/Data1'
mypath = 'F:/Research/High Low Strategy/Data/ALLDATA'
arr = os.listdir(mypath)

final_dat = []
for p in range(len(arr)):
    dat = pd.read_csv(mypath + '/' + arr[p])
    dat.columns = ['Date', 'Open', 'High', 'Low', 'Close']
    dat.index = pd.to_datetime(dat['Date'])
    dat = dat.iloc[:, 1: 5]
    dat['temp'] = dat['Close'].shift(lag_val)

    dat['entry_HC_Spread'] = (
                abs((dat['High'] / dat['Close'].shift(lag_val) - 1).rolling(MA_val).mean()) * entry_thresh).shift(1)
    dat['entry_LC_Spread'] = (
                abs((dat['Low'] / dat['Close'].shift(lag_val) - 1).rolling(MA_val).mean()) * entry_thresh).shift(1)

    dat['exit_HC_Spread'] = (
                abs((dat['High'] / dat['Close'].shift(lag_val) - 1).rolling(MA_val).mean()) * exit_thresh).shift(1)
    dat['exit_LC_Spread'] = (
                abs((dat['Low'] / dat['Close'].shift(lag_val) - 1).rolling(MA_val).mean()) * exit_thresh).shift(1)

    dat['long_entry'] = 0
    dat['long_exit'] = 0
    dat = dat.dropna()

    myindex1 = dat.loc[(dat['Open'] > dat['temp'])].index
    dat['long_entry'].loc[myindex1] = dat['Open'].loc[myindex1] + (
                dat['Open'].loc[myindex1] * dat['entry_HC_Spread'].loc[myindex1])
    dat['long_exit'].loc[myindex1] = dat['Open'].loc[myindex1] + (
                dat['Open'].loc[myindex1] * dat['exit_HC_Spread'].loc[myindex1])

    myindex1 = dat.loc[(dat['long_entry'] == 0)].index
    dat['long_entry'].loc[myindex1] = dat['temp'].loc[myindex1] + (
                dat['temp'].loc[myindex1] * dat['entry_HC_Spread'].loc[myindex1])
    dat['long_exit'].loc[myindex1] = dat['temp'].loc[myindex1] + (
                dat['temp'].loc[myindex1] * dat['exit_HC_Spread'].loc[myindex1])

    dat['short_entry'] = 0
    dat['short_exit'] = 0
    myindex1 = dat.loc[(dat['Open'] < dat['temp'])].index
    dat['short_entry'].loc[myindex1] = dat['Open'].loc[myindex1] - (
                dat['Open'].loc[myindex1] * dat['entry_LC_Spread'].loc[myindex1])
    dat['short_exit'].loc[myindex1] = dat['Open'].loc[myindex1] - (
                dat['Open'].loc[myindex1] * dat['exit_LC_Spread'].loc[myindex1])

    myindex1 = dat.loc[(dat['short_entry'] == 0)].index
    dat['short_entry'].loc[myindex1] = dat['temp'].loc[myindex1] - (
                dat['temp'].loc[myindex1] * dat['entry_LC_Spread'].loc[myindex1])
    dat['short_exit'].loc[myindex1] = dat['temp'].loc[myindex1] - (
                dat['temp'].loc[myindex1] * dat['exit_LC_Spread'].loc[myindex1])

    dat = dat.dropna()
    dat['HC_Ret'] = 0
    dat['LC_Ret'] = 0
    dat.loc[dat['High'] > dat['long_exit'], 'HC_Ret'] = dat['long_exit'] / dat['long_entry'] - 1
    dat.loc[dat['Low'] < dat['short_exit'], 'LC_Ret'] = -1 * (dat['short_exit'] / dat['short_entry'] - 1)

    myindex = dat.loc[dat['HC_Ret'] == 0].index
    dat['HC_Ret'].loc[myindex] = dat['Close'].loc[myindex] / dat['long_entry'].loc[myindex] - 1

    myindex = dat.loc[dat['LC_Ret'] == 0].index
    dat['LC_Ret'].loc[myindex] = -1 * (dat['Close'].loc[myindex] / dat['short_entry'].loc[myindex] - 1)

    dat.loc[dat['High'] < dat['long_entry'], 'HC_Ret'] = 'NaN'
    dat.loc[dat['Low'] > dat['short_entry'], 'LC_Ret'] = 'NaN'

    dat = dat[['HC_Ret', 'LC_Ret']]
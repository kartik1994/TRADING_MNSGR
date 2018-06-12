import numpy as np
import math
import time
import timeit
import random
##DB Instance
# from pymongo import MongoClient
#
# client = MongoClient('localhost', 27017)
# db = client.currencyData
#
# from CURRENCY_FOREX_2018 import curr_name
# from docutils.nodes import entry
import random
from IBWrapper import IBWrapper, contract
from ib.ext.EClientSocket import EClientSocket
from ib.ext.ScannerSubscription import ScannerSubscription
from ib.opt import ibConnection, message
import warnings
warnings.filterwarnings('ignore',category=DeprecationWarning)
import warnings

from functools import lru_cache as cache
# @cache(maxsize=None)

# from numba import jit, autojit


# with warnings.catch_warnings():
#     warnings.filterwarnings("ignore", category=DeprecationWarning)
#     import imp
# import pip

import time
import csv
import timeit
import random
import pandas as pd
from datetime import datetime, timedelta
import threading
from threading import Thread
import multiprocessing
from multiprocessing import Process
# from flask import Flask, url_for, request, render_template, redirect
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler()
import openpyxl

###############################################

callback = IBWrapper()
tws = EClientSocket(callback)
host = ""
port = 7496
clientId = 100
create = contract()
callback.initiate_variables()

acc = "DU228380"



# hl_curr_ny = 'YES'


df_common_inputs = pd.read_excel('C:/database/FX_DAILY/FOREX_settings.xlsx', 'common_inputs')
df_london = pd.read_excel('C:/database/FX_DAILY/FOREX_settings.xlsx', 'LONDON_TRADES')
df_o_val = pd.read_excel('C:/database/FX_DAILY/FOREX_settings.xlsx', 'LONDON_ENTRY')
df_switch = pd.read_excel('C:/database/FX_DAILY/FOREX_settings.xlsx', 'LONDON_SWITCH')
commonwealth_curr = ['GBP', 'AUD', 'NZD', 'EUR']


def conn():
    status = tws.isConnected()
    if status == False:
        print("######### $$$$$$$$$$$$$$$$$$ RECONNECTING TWS SESSION   $$$$$$$$$$$$$$$$$$############")
        tws.eConnect(host, port, clientId)
        # print("######### $$$$$$$$$$$$$$$$$$$ TWS CONNECTED   $$$$$$$$$$$$$$$$$$############")
    # else:

    # print("######### $$$$$$$$$$$$$$$$$$$ TWS CONNECTION INTACT  $$$$$$$$$$$$$$$$$$############")
    return


conn()
tws.setServerLogLevel(5)

def disconn():
    tws.eDisconnect()
    tws.eDisconnect()
    # print("######### $$$$$$$$$$$$$$$$$$$ TWS DISCONNECTED   $$$$$$$$$$$$$$$$$$############")
    return


def error_handler(msg):
    """Handles the capturing of error messages"""
    print("Server Error: %s" % msg)


def reply_handler(msg):
    """Handles of server replies"""
    print("Server Response: %s, %s" % (msg.typeName, msg))


def contract1(sym, sec, exc, curr, blank, blank2, expiry, mul):
    contract_Details = create.create_contract(sym, sec, exc, curr, blank, blank2, expiry, mul)
    return contract_Details


def realtime(contract_Details):
    data = pd.DataFrame()
    while data.empty:
        conn()
        a = random.sample(range(60001, 60300), 40)
        b = random.sample(range(60301, 60600), 40)
        random.shuffle(a)
        random.shuffle(b)
        tickerId = a[0] + b[0]
        # #print(datetime.now())
        tws.reqRealTimeBars(tickerId,
                            contract_Details,
                            5,
                            "MIDPOINT",
                            0)
        time.sleep(2)
        data = list(callback.real_timeBar)

        for i in range(0, len(data)):
            data[i] = tuple(data[i])

        data = pd.DataFrame.from_records(data,
                                         columns=["reqId", "time", "open", "high", "low", "close", "volume", "wap",
                                                  "count"])
        data = data[data.reqId == tickerId]
    data = data.tail(1)
    data = data.rename(index=str, columns={"time": "date"})
    return data


def tickerId():
    a = random.sample(range(60001, 90000), 2000)
    b = random.sample(range(1, 10000), 40)
    random.shuffle(a)
    random.shuffle(b)
    tickerId = a[0] + b[0]
    return tickerId


def historical(date, con, totaldays, Id1,type):
    # date = (datetime.now() + timedelta(3)).strftime("%Y%m%d") + fortime

    # date = datetime.now().strftime("%Y%m%d") + fortime
    df = pd.DataFrame()
    while df.empty:
        print("trying")
        Id1=Id1+1
        tws.reqHistoricalData(Id1, con, date,
                              totaldays,
                              '5 mins',   ###  5 min
                              type,
                              1,
                              1)
        time.sleep(2)
        df = list(callback.historical_Data)
        for k in range(0, len(df)):
            df[k] = tuple(df[k])
        df = pd.DataFrame(df,
                          columns=["reqId", "date", "open",
                                   "high", "low", "close",
                                   "volume", "count", "WAP",
                                   "hasGaps"])
        df = df[df.reqId == Id1]

    # tws.cancelHistoricalData(Id1)
    data_df = pd.DataFrame()
    data_df = df[:-1]
    # data_df=data_df.tail(20)
    tws.cancelHistoricalData(Id1)
    # df=df.tail(31)
    return data_df




    ####### roll dates fun ############

from datetime import datetime, timedelta

# def roll_date(datetime):
#     print(datetime)
#     date1 = str(datetime) # eg: "20180522 13:30:00"
#     today = datetime.strptime(date1, '%Y%m%d %H:%M:%S')
#     new_date = today - timedelta(days=20)
#     new_date = new_date.strftime('%Y%m%d %H:%M:%S')
#     print(new_date)
#     return new_date





def main(contract,id,df_c1,path,type):

    lookback_limit=1 ### for rolling date from code
    hist_lookback="1 D"   #### historical data lookback from IB
    # lookback_period_in_days=100  ### number of days' data
    count=50
    date = datetime.now().strftime("%Y%m%d 00:00:00")
    ### start fetching data from current date

    #date="20180418 03:16:00"

    #days=[0]

    i=0
    while i<count:

        df=historical(date,contract,hist_lookback,id,type)
        df=df[:-1]
        df=df[["date","open","high","low","close"]]
        df_c1=df_c1.append(df,ignore_index=True)
        df_c1=df_c1.drop_duplicates()
        df_c1=df_c1[df_c1.date.str.contains("finished") == False]
        df=pd.DataFrame()


        prev_date = datetime.strptime(date, '%Y%m%d %H:%M:%S')
        date = prev_date - timedelta(days=lookback_limit)
        date = date.strftime('%Y%m%d %H:%M:%S')
        #days.append(days[-1]+1)
        print(date)  #### get date 20 days behind and make it as your starting point for the new iteration
        i=i+1
    #print(df_c1)
    df_c1=df_c1.sort_values(by='date')
    df_c1.to_html(path,col_space=200,justify ="center",index=False)


    return



def universe():

    type="MIDPOINT"
    df_audnzd = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    contract_audnzd = create.create_contract("AUD", "CASH", "IDEALPRO", "NZD", "", "", "", "")
    path="C:/REPORTS/audnzd.html"
    Thread(target=main,args=(contract_audnzd,1,df_audnzd,path,type)).start()

    # df_eurnok = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_eurnok = create.create_contract("EUR", "CASH", "IDEALPRO", "NOK", "", "", "", "")
    # path="C:/REPORTS/eurnok.html"
    # Thread(target=main,args=(contract_eurnok,2,df_eurnok,path,type)).start()
    #
    # df_eursek = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_eursek = create.create_contract("EUR", "CASH", "IDEALPRO", "SEK", "", "", "", "")
    # path = "C:/REPORTS/eursek.html"
    # Thread(target=main, args=(contract_eursek, 3, df_eursek, path,type)).start()
    #
    # df_chfnok = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_chfnok = create.create_contract("CHF", "CASH", "IDEALPRO", "NOK", "", "", "", "")
    # path = "C:/REPORTS/chfnok.html"
    # Thread(target=main, args=(contract_chfnok, 4, df_chfnok, path,type)).start()
    #
    # df_chfsek = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_chfsek = create.create_contract("CHF", "CASH", "IDEALPRO", "SEK", "", "", "", "")
    # path = "C:/REPORTS/chfsek.html"
    # Thread(target=main, args=(contract_chfsek, 5, df_chfsek, path,type)).start()
    #
    # df_gbpnok = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_gbpnok = create.create_contract("GBP", "CASH", "IDEALPRO", "NOK", "", "", "", "")
    # path = "C:/REPORTS/gbpnok.html"
    # Thread(target=main, args=(contract_gbpnok, 6, df_gbpnok, path,type)).start()
    #
    # df_gbpsek = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_gbpsek = create.create_contract("GBP", "CASH", "IDEALPRO", "SEK", "", "", "", "")
    # path = "C:/REPORTS/gbpsek.html"
    # Thread(target=main, args=(contract_gbpsek, 7, df_gbpsek, path,type)).start()
    #
    # df_noksek = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_noksek = create.create_contract("NOK", "CASH", "IDEALPRO", "SEK", "", "", "", "")
    # path = "C:/REPORTS/noksek.html"
    # Thread(target=main, args=(contract_noksek, 8, df_noksek, path,type)).start()
    #
    # df_eurnzd = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_eurnzd = create.create_contract("EUR", "CASH", "IDEALPRO", "NZD", "", "", "", "")
    # path = "C:/REPORTS/eurnzd.html"
    # Thread(target=main, args=(contract_eurnzd, 9, df_eurnzd, path,type)).start()
    #
    # df_nzdchf = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_nzdchf = create.create_contract("NZD", "CASH", "IDEALPRO", "CHF", "", "", "", "")
    # path = "C:/REPORTS/nzdchf.html"
    # Thread(target=main, args=(contract_nzdchf, 10, df_nzdchf, path,type)).start()





















    # type = "ASK"
    # df_audnzd = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_audnzd = create.create_contract("AUD", "CASH", "IDEALPRO", "NZD", "", "", "", "")
    # path = "C:/REPORTS/audnzdask.html"
    # Thread(target=main, args=(contract_audnzd, 12, df_audnzd, path, type)).start()
    #
    # df_eurnok = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_eurnok = create.create_contract("EUR", "CASH", "IDEALPRO", "NOK", "", "", "", "")
    # path = "C:/REPORTS/eurnokask.html"
    # Thread(target=main, args=(contract_eurnok, 13, df_eurnok, path, type)).start()
    #
    # df_eursek = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_eursek = create.create_contract("EUR", "CASH", "IDEALPRO", "SEK", "", "", "", "")
    # path = "C:/REPORTS/eursekask.html"
    # Thread(target=main, args=(contract_eursek, 14, df_eursek, path, type)).start()
    #
    # df_chfnok = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_chfnok = create.create_contract("CHF", "CASH", "IDEALPRO", "NOK", "", "", "", "")
    # path = "C:/REPORTS/chfnokask.html"
    # Thread(target=main, args=(contract_chfnok, 15, df_chfnok, path, type)).start()
    #
    # df_chfsek = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_chfsek = create.create_contract("CHF", "CASH", "IDEALPRO", "SEK", "", "", "", "")
    # path = "C:/REPORTS/chfsekask.html"
    # Thread(target=main, args=(contract_chfsek, 16, df_chfsek, path, type)).start()
    #
    # df_gbpnok = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_gbpnok = create.create_contract("GBP", "CASH", "IDEALPRO", "NOK", "", "", "", "")
    # path = "C:/REPORTS/gbpnokask.html"
    # Thread(target=main, args=(contract_gbpnok, 17, df_gbpnok, path, type)).start()
    #
    # df_gbpsek = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_gbpsek = create.create_contract("GBP", "CASH", "IDEALPRO", "SEK", "", "", "", "")
    # path = "C:/REPORTS/gbpsekask.html"
    # Thread(target=main, args=(contract_gbpsek, 18, df_gbpsek, path, type)).start()
    #
    # df_noksek = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_noksek = create.create_contract("NOK", "CASH", "IDEALPRO", "SEK", "", "", "", "")
    # path = "C:/REPORTS/noksekask.html"
    # Thread(target=main, args=(contract_noksek, 19, df_noksek, path, type)).start()
    #
    # df_eurnzd = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_eurnzd = create.create_contract("EUR", "CASH", "IDEALPRO", "NZD", "", "", "", "")
    # path = "C:/REPORTS/eurnzdask.html"
    # Thread(target=main, args=(contract_eurnzd, 20, df_eurnzd, path, type)).start()
    #
    # df_nzdchf = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_nzdchf = create.create_contract("NZD", "CASH", "IDEALPRO", "CHF", "", "", "", "")
    # path = "C:/REPORTS/nzdchfask.html"
    # Thread(target=main, args=(contract_nzdchf, 21, df_nzdchf, path, type)).start()
    #









    # type = "BID"
    # df_audnzd = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_audnzd = create.create_contract("AUD", "CASH", "IDEALPRO", "NZD", "", "", "", "")
    # path = "C:/REPORTS/audnzdbid.html"
    # Thread(target=main, args=(contract_audnzd, 22, df_audnzd, path, type)).start()
    #
    # df_eurnok = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_eurnok = create.create_contract("EUR", "CASH", "IDEALPRO", "NOK", "", "", "", "")
    # path = "C:/REPORTS/eurnokbid.html"
    # Thread(target=main, args=(contract_eurnok, 23, df_eurnok, path, type)).start()
    #
    # df_eursek = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_eursek = create.create_contract("EUR", "CASH", "IDEALPRO", "SEK", "", "", "", "")
    # path = "C:/REPORTS/eursekbid.html"
    # Thread(target=main, args=(contract_eursek, 24, df_eursek, path, type)).start()
    #
    # df_chfnok = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_chfnok = create.create_contract("CHF", "CASH", "IDEALPRO", "NOK", "", "", "", "")
    # path = "C:/REPORTS/chfnokbid.html"
    # Thread(target=main, args=(contract_chfnok, 25, df_chfnok, path, type)).start()
    #
    # df_chfsek = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_chfsek = create.create_contract("CHF", "CASH", "IDEALPRO", "SEK", "", "", "", "")
    # path = "C:/REPORTS/chfsekbid.html"
    # Thread(target=main, args=(contract_chfsek, 26, df_chfsek, path, type)).start()
    #
    # df_gbpnok = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_gbpnok = create.create_contract("GBP", "CASH", "IDEALPRO", "NOK", "", "", "", "")
    # path = "C:/REPORTS/gbpnokbid.html"
    # Thread(target=main, args=(contract_gbpnok, 27, df_gbpnok, path, type)).start()
    #
    # df_gbpsek = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_gbpsek = create.create_contract("GBP", "CASH", "IDEALPRO", "SEK", "", "", "", "")
    # path = "C:/REPORTS/gbpsekbid.html"
    # Thread(target=main, args=(contract_gbpsek, 28, df_gbpsek, path, type)).start()
    #
    # df_noksek = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_noksek = create.create_contract("NOK", "CASH", "IDEALPRO", "SEK", "", "", "", "")
    # path = "C:/REPORTS/noksekbid.html"
    # Thread(target=main, args=(contract_noksek, 29, df_noksek, path, type)).start()
    #
    # df_eurnzd = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_eurnzd = create.create_contract("EUR", "CASH", "IDEALPRO", "NZD", "", "", "", "")
    # path = "C:/REPORTS/eurnzdbid.html"
    # Thread(target=main, args=(contract_eurnzd, 30, df_eurnzd, path, type)).start()
    #
    # df_nzdchf = pd.DataFrame(columns=['date', "open", "high", "low", "close"])
    # contract_nzdchf = create.create_contract("NZD", "CASH", "IDEALPRO", "CHF", "", "", "", "")
    # path = "C:/REPORTS/nzdchfbid.html"
    # Thread(target=main, args=(contract_nzdchf, 31, df_nzdchf, path, type)).start()
    # return


# Thread(target=universe).start()
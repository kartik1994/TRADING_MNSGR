from _cffi_backend import typeof

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


from IBWrapper import IBWrapper, contract
from ib.ext.EClientSocket import EClientSocket
from ib.opt import ibConnection, message
import warnings

warnings.filterwarnings('ignore')
from ib.ext.ScannerSubscription import ScannerSubscription
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


###############################################

callback = IBWrapper()
tws = EClientSocket(callback)
host = ""
port = 7496
clientId = 100
create = contract()
callback.initiate_variables()




def conn():
    status = tws.isConnected()
    if status == False:
        # print("######### $$$$$$$$$$$$$$$$$$ RECONNECTING TWS SESSION   $$$$$$$$$$$$$$$$$$############")
        tws.eConnect(host, port, clientId)
        # print("######### $$$$$$$$$$$$$$$$$$$ TWS CONNECTED   $$$$$$$$$$$$$$$$$$############")
    # else:

    # print("######### $$$$$$$$$$$$$$$$$$$ TWS CONNECTION INTACT  $$$$$$$$$$$$$$$$$$############")
    return


def disconn():
    tws.eDisconnect()
    tws.eDisconnect()
    # print("######### $$$$$$$$$$$$$$$$$$$ TWS DISCONNECTED   $$$$$$$$$$$$$$$$$$############")
    return
def contract1(sym, sec, exc, curr, blank, blank2, expiry, mul):
    contract_Details = create.create_contract(sym, sec, exc, curr, blank, blank2, expiry, mul)
    return contract_Details



def tickerId():
    a = random.sample(range(60001, 90000), 2000)
    b = random.sample(range(1, 10000), 40)
    random.shuffle(a)
    random.shuffle(b)
    tickerId = a[0] + b[0]
    return tickerId


def historical(fortime, con, totaldays, Id1):
    date = (datetime.now() + timedelta(3)).strftime("%Y%m%d") + fortime

    # date = datetime.now().strftime("%Y%m%d") + fortime
    df = pd.DataFrame()
    while df.empty:
        # Id1=Id1+1
        tws.reqHistoricalData(Id1, con, date,
                              totaldays,
                              '1 day',
                              "MIDPOINT",
                              0,
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

conn()
tp_buy = 0
tp_buy2 = 0
tp_sell = 0
tp_sell2 = 0

time_ny = ' 00:30:00'
time_ldn = ' 22:30:00'
exeprice = 313.120  #######to_update
params = ['EUR.SEK']
round_tp = 5
lookback = 20
tp1= 0.2
tp2=0.18

# pandas.set_option('display.max_colwidth',100)


def realtime(contract_Details,tickerId):
    data = pd.DataFrame()
    while data.empty:
        conn()
        # a = random.sample(range(60001, 60300), 40)
        # b = random.sample(range(60301, 60600), 40)
        # random.shuffle(a)
        # random.shuffle(b)
        # tickerId = a[0] + b[0]
        # #print(datetime.now())
        tws.reqRealTimeBars(tickerId,
                            contract_Details,
                            5,
                            "ASK",
                            0)
        time.sleep(0.2)
        data = list(callback.real_timeBar)

        for i in range(0, len(data)):
            data[i] = tuple(data[i])

        data = pd.DataFrame.from_records(data,
                                         columns=["reqId", "time", "open", "high", "low", "close", "volume", "wap",
                                                  "count"])
        data = data[data.reqId == tickerId]
        tws.cancelRealTimeBars(tickerId)

    data = data.tail(1)
    data = data.rename(index=str, columns={"time": "date"})
    return data

#
# contract = create.create_contract('NOK', "CASH", "IDEALPRO", 'SEK', '', '', '', '')
# for i in range(20):
#     a = realtime(contract, 251)
#     print(a["close"].iloc[-1])


def mkt_depth(contract, tickerId):
    ask, bid = 1, 1

    attempts = [0]

    while ask == 1 or bid == 1:
        # conn()
        data_mktdepth = pd.DataFrame()
        tickerId = tickerId + 1

        while data_mktdepth.empty:
            # conn()
            tws.reqMktDepth(tickerId, contract, 5)
            attempts.append(attempts[-1] + 1)
            if attempts[-1] > 7:
                print("ATTEMPTING HARDER", attempts[-1])
                sleeptime = 1
                # disconn()
                # conn()
            else:
                sleeptime = 0.3
            time.sleep(sleeptime)



            operation_type = {0: "Insert",
                              1: "Update",
                              2: "Delete", }

            side_type = {0: "Ask",
                         1: "Bid"}

            data_mktdepth = list(callback.update_MktDepth)
            for k in range(0, len(data_mktdepth)):
                data_mktdepth[k] = tuple(data_mktdepth[k])
            data_mktdepth = pd.DataFrame(data_mktdepth,
                                         columns=["tickerId", "position",
                                                  "operation", "side",
                                                  "price", "size"])[-20:]

        data_mktdepth["operation_type"] = data_mktdepth["operation"].map(operation_type)
        data_mktdepth["side_type"] = data_mktdepth["side"].map(side_type)
        # print(data_mktdepth.tail(8))
        # print(data_mktdepth[-10:])
        # ask = data_mktdepth.loc[data_mktdepth["side"] == '1', 'price'].iloc[-1]
        tws.cancelMktDepth(tickerId)
        tws.cancelMktData(tickerId)
        tws.cancelRealTimeBars(tickerId)
        data_mktdepth = data_mktdepth[data_mktdepth.tickerId == tickerId]
        status1 = 'Ask' in data_mktdepth.side_type.values
        status2 = 'Bid' in data_mktdepth.side_type.values
        if status1 == False or status2 == False:
            ask = 1
            bid = 1
        else:
            ask = 0
            bid = 0

    # pd.set_option('display.height', 1000)
    # pd.set_option('display.max_rows', 500)
    # pd.set_option('display.max_columns', 500)
    # pd.set_option('display.width', 1000)

    df_rt=pd.DataFrame()
    df_ask = data_mktdepth.loc[data_mktdepth["side_type"] == 'Ask', ['price', 'size']]
    df_bid = data_mktdepth.loc[data_mktdepth["side_type"] == 'Bid', ['price', 'size']]

    df_ask=df_ask.reset_index(drop=True)
    df_bid=df_bid.reset_index(drop=True)
    df_rt=pd.concat([df_ask,df_bid],axis=1,ignore_index=True)
    df_rt['Date']= [datetime.now().strftime("%Y%m%d %H:%M:%S")]*len(df_rt)
    df_rt.columns=["ASK","ASK_SIZE","BID","BID_SIZE","DATE"]
    df_rt=df_rt[["DATE","ASK","ASK_SIZE","BID","BID_SIZE"]]


    print(df_rt)

    # print(df_rt)


    return df_rt



import pandas as pd



def streaming_data(symbol,id,df):
    contract=create.create_contract(symbol[0:3],"CASH","IDEALPRO",symbol[3:])

    file = pd.read_excel("C:\database\FX_DAILY/FOREX_settings.xlsx", "MKT_DEPTH")
    pause=file["PAUSE"].iloc[-1]

    while pause=="no":
        l2data=mkt_depth(contract,id)
        d = datetime.now().strftime("%Y-%m-%d %H:%M:%S            ")
        # pd.set_option('display.height', 1000)
        # pd.set_option('display.max_rows', 500)
        # pd.set_option('display.max_columns', 500)
        # pd.set_option('display.width', 1000)
        df=df.append(l2data)
        # df = df.append({'DATE': d, "ASK": l2data[0], "BID": l2data[1]}, ignore_index=True)

        # df.loc[-1] = [d, l2data[0],l2data[1], l2data[2],l2data[3]]  # adding a row
        # df.index = df.index + 1  # shifting index
        # df.sort_index(inplace=True)
        # print(df)


        filename = "E:\MKT_DEPTH/" + symbol + ".html"
        df.to_html(filename,col_space=200,justify ="center",index=False)
        file = pd.read_excel("C:\database\FX_DAILY/FOREX_settings.xlsx", "MKT_DEPTH")
        pause = file["PAUSE"].iloc[-1]
        update=file["UPDATE"].iloc[-1]
        if update=="yes":
            d = datetime.now().strftime("%Y%m%d%H%M%S")
            filename="E:\MKT_DEPTH/" + symbol + "_"+d+".csv"
            df.to_csv(filename)


def run_data():
    AUDNZD_df = pd.DataFrame(columns=["DATE", "ASK","ASK_SIZE", "BID","BID_SIZE"])
    Thread(target=streaming_data,args=("AUDNZD",1,AUDNZD_df)).start()

    time.sleep(5)
    NOKSEK_df = pd.DataFrame(columns=["DATE", "ASK","ASK_SIZE", "BID","BID_SIZE"])
    Thread(target=streaming_data,args=("NOKSEK",25,NOKSEK_df)).start()

    EURSEK_df = pd.DataFrame(columns=["DATE", "ASK","ASK_SIZE", "BID","BID_SIZE"])
    Thread(target=streaming_data,args=("EURSEK",50,EURSEK_df)).start()

    EURSEK_df = pd.DataFrame(columns=["DATE", "ASK", "ASK_SIZE", "BID", "BID_SIZE"])
    Thread(target=streaming_data, args=("EURSEK", 50, EURSEK_df)).start()

# run_data()
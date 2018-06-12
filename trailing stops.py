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
import time
from datetime import datetime
from IBWrapper import IBWrapper, contract
from ib.ext.EClientSocket import EClientSocket
from ib.ext.ScannerSubscription import ScannerSubscription
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
commonwealth_curr = ['GBP', 'AUD', 'NZD', 'EUR']
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
def ask_bid(contract, tickerId):
    tickedId = int(tickerId)
    # tws.cancelMktData(tickedId)
    tick = contract
    ask = 1
    bid = 1
    attempts = [0]
    while ask == 1 and bid == 1:
        # sleeptime=0.4
        conn()
        tickedId = int(tickerId + 1)
        tick_data1 = pd.DataFrame()
        while tick_data1.empty:
            instance = attempts[-1]
            if instance > 4:
                conn()
                print("ATTEMPTING HARDER:", instance)
                tickedId = int(tickerId + 1)
                tws.reqMktData(tickedId, tick, "", 1)
                # print("ask/bid unavailable at the moment")
                sleeptime = 1
                time.sleep(sleeptime)
            else:
                conn()
                tickedId = int(tickerId + 1)
                tws.reqMktData(tickedId, tick, "", 1)
                sleeptime = 0.4
                time.sleep(sleeptime)
            attempts.append(attempts[-1] + 1)
            tick_data1 = list(callback.tick_Price)
            for k in range(0, len(tick_data1)):
                tick_data1[k] = tuple(tick_data1[k])
            tick_data1 = pd.DataFrame(tick_data1,
                                      columns=['tickerId', 'field', 'price', 'canAutoExecute'])
            tick_data1 = tick_data1[tick_data1.tickerId == tickedId]
            tws.cancelMktData(tickedId)
        tick_type = {
            1: "BID PRICE",
            2: "ASK PRICE",
        }
        time.sleep(sleeptime / 2)
        tick_data1["Type"] = tick_data1["field"].map(tick_type)
        # #print(tick_data1)
        a = tick_data1
        # #print(a)
        status1 = 'ASK PRICE' in tick_data1.Type.values
        status2 = 'BID PRICE' in tick_data1.Type.values
        # time.sleep(1)
        # #print("ASK", status1, "BID", status2)
        if status1 == False or status2 == False:
            # print("ASK AND BID UNAVAILABLE")
            ask = 1
            bid = 1
        else:
            # print("ASK AND BID AVAILABLE")
            ask = a.loc[a["Type"] == 'ASK PRICE', 'price'].iloc[-1]
            bid = a.loc[a["Type"] == 'BID PRICE', 'price'].iloc[-1]
            ask = float(ask)
            bid = float(bid)
            # ask = a.loc[a["Type"] == 'ASK PRICE', 'price'].iloc[-1]
            # bid = a.loc[a["Type"] == 'BID PRICE', 'price'].iloc[-1]
            # ask=float(ask)
            # bid=float(bid)
        # tws.cancelMktData(tickedId)
    # print(ask,bid)
    # print(attempts)
    conn()
    tws.cancelMktData(tickedId)
    mid = float((ask + bid) / 2)
    # #print("OBTAINED CORRECT DETAILS FOR")
    return ask, bid, mid
conn()
def generateNumber(num):
    order_id = []
    tws.reqIds(1)
    while not order_id:
        time.sleep(0.1)
        order_id = callback.next_ValidId
        break
    mylist = []
    for i in range(num):
        mylist.append(order_id)
        order_id = order_id + 1
    return mylist


conn()
order_id=generateNumber(2)
contract_info=contract1("AUD","CASH","IDEALPRO","NZD","","","","")
#order_info = create.create_order(acc, "LMT", 10000, "BUY", 10.000, False, False, None,0,0)
                                                                  # 22% price #         # 15% price#
order_info = create.create_order(acc, "TRAIL LIMIT", 10000, "SELL",1.0930, True, False,None,1.09270,0.001,True,0.0)
                                                                                                #trail perc #
tws.placeOrder(int(order_id[0]), contract_info, order_info)

# order_info = create.create_order(acc, "TRAIL LIMIT", 10000, "SELL", "0.01", True, False, None,0,0,0.02)
# tws.placeOrder(int(order_id[1]), contract_info, order_info)


conn()
order_id = generateNumber(2)
                                                        # 22% price #         # 15% price#
order_info = create.create_order(acc, "LMT", 10000, "SELL",1.0930, True, False,None,"","",True,"")
tws.placeOrder(int(order_id[0]), contract_info, order_info)                                                                                   #trail perc #


order_info = create.create_order(acc, "TRAIL LIMIT", 10000, "SELL",1.0930, True, False,None,1.09270,0.001,True,0.0)
                                                                                                #trail perc #
tws.placeOrder(int(order_id[0]), contract_info, order_info)


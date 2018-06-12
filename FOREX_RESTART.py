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

sched = BackgroundScheduler()
import openpyxl

###############################################

callback = IBWrapper()
tws = EClientSocket(callback)
host = ""
port = 7497
clientId = 100
create = contract()
callback.initiate_variables()

acc = "DU228380"
total_cap = 2000000
Core_port_levrg = 1
LDN_curr_levrg = 16
NY_curr_levrg = 10

# transformation_1_wghts = 0.03816
# transformation_2_wghts = 0.03669
# metaphor_wghts = 0.06162
# # camouflage_wghts =
# fundamentals_wghts = 0.06747
#
# camouflage_intraday_TP = 0.05
# camouflage_EOD_TP = 0.03
#
# transformation_1 = 'YES'
# transformation_2 = 'YES'
# metaphor = 'YES'
# camouflage = 'YES'
# fundamentals = 'YES'
# hl_eqty = 'YES'
# hl_curr_ldn = 'YES'
# hl_curr_ny = 'YES'


df_common_inputs = pd.read_excel('E:/database/FX_DAILY/FOREX_settings.xlsx', 'common_inputs')
df_london = pd.read_excel('E:/database/FX_DAILY/FOREX_settings.xlsx', 'LONDON_TRADES')
df_o_val = pd.read_excel('E:/database/FX_DAILY/FOREX_settings.xlsx', 'LONDON_ENTRY')
df_switch = pd.read_excel('E:/database/FX_DAILY/FOREX_settings.xlsx', 'LONDON_SWITCH')
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


def historical(fortime, con, totaldays, Id1):
    # date = (datetime.now() + timedelta(2)).strftime("%Y%m%d")

    date = datetime.now().strftime("%Y%m%d") + fortime
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

    data_df = df[:-1]
    # data_df=data_df.tail(20)

    # df=df.tail(31)
    return data_df


def ask_bid(contract, tickerId):
    tickedId = int(tickerId)

    tick = contract

    ask = 1
    bid = 1
    while ask == 1 and bid == 1:
        conn()
        tick_data1 = pd.DataFrame()
        while tick_data1.empty:
            tws.reqMktData(tickedId, tick, "", False)
            time.sleep(2)
            tick_data1 = list(callback.tick_Price)
            for k in range(0, len(tick_data1)):
                tick_data1[k] = tuple(tick_data1[k])
            tick_data1 = pd.DataFrame(tick_data1,
                                      columns=['tickerId', 'field', 'price', 'canAutoExecute'])
            tick_data1 = tick_data1[tick_data1.tickerId == tickedId]
        tick_type = {0: "BID SIZE",
                     1: "BID PRICE",
                     2: "ASK PRICE",
                     3: "ASK SIZE",
                     4: "LAST PRICE",
                     5: "LAST SIZE",
                     6: "HIGH",
                     7: "LOW",
                     8: "VOLUME",
                     9: "CLOSE PRICE",
                     10: "BID OPTION COMPUTATION",
                     11: "ASK OPTION COMPUTATION",
                     12: "LAST OPTION COMPUTATION",
                     13: "MODEL OPTION COMPUTATION",
                     14: "OPEN_TICK",
                     15: "LOW 13 WEEK",
                     16: "HIGH 13 WEEK",
                     17: "LOW 26 WEEK",
                     18: "HIGH 26 WEEK",
                     19: "LOW 52 WEEK",
                     20: "HIGH 52 WEEK",
                     21: "AVG VOLUME",
                     22: "OPEN INTEREST",
                     23: "OPTION HISTORICAL VOL",
                     24: "OPTION IMPLIED VOL",
                     27: "OPTION CALL OPEN INTEREST",
                     28: "OPTION PUT OPEN INTEREST",
                     29: "OPTION CALL VOLUME"}

        tick_data1["Type"] = tick_data1["field"].map(tick_type)
        # #print(tick_data1)
        a = tick_data1
        # #print(a)
        status1 = 'ASK PRICE' in tick_data1.Type.values
        status2 = 'BID PRICE' in tick_data1.Type.values
        time.sleep(1)
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
    tws.cancelMktData(tickedId)

    # #print("OBTAINED CORRECT DETAILS FOR")
    return ask, bid, tickedId


def open_pos():
    for i in range(0, 5):
        tws.reqPositions()
        dat = list(callback.update_Position)
        if len(dat) == 0:
            # print("empty dat")
            dat = pd.DataFrame()
            # time.sleep(30-15*i)
            time.sleep(0.5)

        else:
            for k in range(0, len(dat)):
                dat[k] = tuple(dat[k])
            dat = pd.DataFrame.from_records(dat,
                                            columns=['Account', 'Contract ID', 'Currency', 'Exchange', 'Expiry',
                                                     'Include Expired', 'Local Symbol', 'Multiplier', 'Right',
                                                     'Security Type', 'Strike', 'Symbol', 'Trading Class',
                                                     'Position', 'Average Cost'])

            dat[dat["Account"] == 'DU536394']
            break

    return dat


def ask_bid_last(contract, tickerId):
    tickedId = int(tickerId)
    tick = contract
    ask = 1
    bid = 1
    last = 1
    while ask == 1 and bid == 1 and last == 1:
        conn()
        tickedId = tickedId + 1
        tick_data1 = pd.DataFrame()
        while tick_data1.empty:
            tws.reqMktData(tickedId, tick, "", False)
            time.sleep(2)
            tick_data1 = list(callback.tick_Price)
            for k in range(0, len(tick_data1)):
                tick_data1[k] = tuple(tick_data1[k])
            tick_data1 = pd.DataFrame(tick_data1,
                                      columns=['tickerId', 'field', 'price', 'canAutoExecute'])
            tick_data1 = tick_data1[tick_data1.tickerId == tickedId]
        tick_type = {0: "BID SIZE",
                     1: "BID PRICE",
                     2: "ASK PRICE",
                     3: "ASK SIZE",
                     4: "LAST PRICE",
                     5: "LAST SIZE",
                     6: "HIGH",
                     7: "LOW",
                     8: "VOLUME",
                     9: "CLOSE PRICE",
                     10: "BID OPTION COMPUTATION",
                     11: "ASK OPTION COMPUTATION",
                     12: "LAST OPTION COMPUTATION",
                     13: "MODEL OPTION COMPUTATION",
                     14: "OPEN_TICK",
                     15: "LOW 13 WEEK",
                     16: "HIGH 13 WEEK",
                     17: "LOW 26 WEEK",
                     18: "HIGH 26 WEEK",
                     19: "LOW 52 WEEK",
                     20: "HIGH 52 WEEK",
                     21: "AVG VOLUME",
                     22: "OPEN INTEREST",
                     23: "OPTION HISTORICAL VOL",
                     24: "OPTION IMPLIED VOL",
                     27: "OPTION CALL OPEN INTEREST",
                     28: "OPTION PUT OPEN INTEREST",
                     29: "OPTION CALL VOLUME"}
        tick_data1["Type"] = tick_data1["field"].map(tick_type)
        # #print(tick_data1)
        a = tick_data1
        # #print(a)
        status1 = 'ASK PRICE' in tick_data1.Type.values
        status2 = 'BID PRICE' in tick_data1.Type.values
        status3 = 'LAST PRICE' in tick_data1.Type.values

        time.sleep(1)
        # #print("ASK", status1, "BID", status2)
        if status1 == False or status2 == False or status3 == False:
            # print("ASK AND BID UNAVAILABLE")
            ask = 1
            bid = 1
            last = 1
        else:
            # print("ASK AND BID AVAILABLE")
            ask = a.loc[a["Type"] == 'ASK PRICE', 'price'].iloc[-1]
            bid = a.loc[a["Type"] == 'BID PRICE', 'price'].iloc[-1]
            last = a.loc[a["Type"] == 'LAST PRICE', 'price'].iloc[-1]
            ask = float(ask)
            bid = float(bid)
            last = float(last)
            # ask = a.loc[a["Type"] == 'ASK PRICE', 'price'].iloc[-1]
            # bid = a.loc[a["Type"] == 'BID PRICE', 'price'].iloc[-1]
            # ask=float(ask)
            # bid=float(bid)
    # #print("OBTAINED CORRECT DETAILS FOR")
    return ask, bid, last


conn()


######capital and weight#######################################

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


def orderidfun(acc, contract, type, exitidlist, loops):
    exit_signal = "null"

    # loops = loops
    contract_info = contract
    # asset_type = type
    # if asset_type == 'LONG':
    #     exit_signal = 'SELL'
    # elif asset_type == 'SHORT':
    #     exit_signal = 'BUY'

    sellidlist = generateNumber(loops)
    while sellidlist[0] == exitidlist[-1][0]:
        sellidlist = generateNumber(loops)
    for i in sellidlist:
        order_info = create.create_order(acc, "LMT", 10000, "SELL", 10.000, False, False, None)
        tws.placeOrder(int(i), contract_info, order_info)

    buyidlist = generateNumber(loops)

    while buyidlist[0] == sellidlist[0]:
        buyidlist = generateNumber(loops)

    for i in buyidlist:
        order_info = create.create_order(acc, "LMT", 10000, "BUY", 10.000, False, False, None)
        tws.placeOrder(int(i), contract_info, order_info)

    loops = 1
    # exitidlist = generateNumber(loops)
    #
    # while exitidlist[0] == buyidlist[0]:
    #     exitidlist = generateNumber(loops)
    #
    # for i in exitidlist:
    #     order_info = create.create_order(acc, "LMT", 10000, exit_signal, 10.000, False, False, None)
    #     tws.placeOrder(int(i), contract_info, order_info)

    return sellidlist, buyidlist


london_list = ["AUD.NZD", "CHF.NOK", "CHF.SEK", "NZD.CHF", "GBP.SEK", "EUR.NZD", "EUR.NOK", "EUR.SEK", "GBP.NOK",
                   "NOK.SEK"]



def LONDON(params,ids,tickerId):
    df_gtd = pd.read_excel('E:/database/FX_DAILY/FOREX_settings.xlsx', 'EXIT_GTD')
    df_london = pd.read_csv("E:/log_london.csv")
    dat = open_pos()
    condition1 = "NOT MET"
    tp_buy=float(df_london.loc[df_london.CURRENCY==params[0],"TP_BUY"].iloc[-1])
    tp_sell = float(df_london.loc[df_london.CURRENCY == params[0], "TP_SELL"].iloc[-1])
    remainqty=int(df_london.loc[df_london.CURRENCY == params[0], "ENTRY_REMAIN"].iloc[-1])
    tp_buy2=float(df_london.loc[df_london.CURRENCY == params[0], "TP_BUY2"].iloc[-1])
    tp_sell2 = float(df_london.loc[df_london.CURRENCY == params[0], "TP_SELL2"].iloc[-1])
    buy_qty=int(df_london.loc[df_london.CURRENCY == params[0], "BUY_QTY"].iloc[-1])
    sell_qty = int(df_london.loc[df_london.CURRENCY == params[0], "SELL_QTY"].iloc[-1])

    exit_sell_list = [tp_sell, "null", "null", "null", "null"]
    exit_buy_list = [tp_buy, "null", "null", "null", "null"]

    if (dat.empty) or (dat[(dat["Local Symbol"] == params[0])].empty) or (
            int(dat[(dat["Local Symbol"] == params[0])].iloc[-1]['Position']) == 0):
        pos = 0
        # print("NO ENTRY FOR", params[0])

        condition_buy = "NOT FULFILLED"
        condition_sell = "NOT FULFILLED"
    else:
        exp_time = str(df_common_inputs["GTD"].iloc[-1])

        ########################################GTD EXPDATE########################################################################
        week_day = datetime.now().weekday()

        if (week_day == 4):

            num = int(df_gtd.loc[df_gtd.MKT == 'LONDON', "FRIDAY"].iloc[-1])
            exp_date1 = datetime.now() + timedelta(days=num)  ##changed for christmas&new year holiday
            exp_date1 = exp_date1.strftime('%Y%m%d') + " " + exp_time


        elif week_day == 5:
            num = int(df_gtd.loc[df_gtd.MKT == 'LONDON', "FRIDAY"].iloc[-1]) - 1
            exp_date1 = datetime.now() + timedelta(days=num)  ##changed for christmas&new year holiday
            exp_date1 = exp_date1.strftime('%Y%m%d') + " " + exp_time

        else:
            ###### consider all possible days from excel ###
            if week_day == 0:
                num = int(df_gtd.loc[df_gtd.MKT == 'LONDON', "MONDAY"].iloc[-1])
            elif week_day == 1:
                num = int(df_gtd.loc[df_gtd.MKT == 'LONDON', "TUESDAY"].iloc[-1])
            elif week_day == 2:
                num = int(df_gtd.loc[df_gtd.MKT == 'LONDON', "WEDNESDAY"].iloc[-1])
            elif week_day == 3:
                num = int(df_gtd.loc[df_gtd.MKT == 'LONDON', "THURSDAY"].iloc[-1])

            exp_date1 = datetime.now() + timedelta(days=num)
            exp_date1 = exp_date1.strftime('%Y%m%d') + " " + exp_time

        ################################################################################################################
        pos = int(dat[(dat["Local Symbol"] == params[0])].iloc[-1]['Position'])
        round1 = 4
        condition_buy = "NOT FULFILLED"
        condition_sell = "NOT FULFILLED"

        actual_tp_buy = tp_buy
        actual_tp_sell = tp_sell
        while pos != 0:
            conn()
            print("### CONSTANTLY CHECKING FOR CONDITIONS ###")
            ###############sleep for regular mkt close############
            ### sleep during weekend if code is initiated during weekend #############
            currtime = datetime.now().strftime("%Y%m%d %H:%M:%S")
            week_day = datetime.now().weekday()

            if week_day == 4 and currtime[-8:] >= "16:59:50":
                wakeuptime = ((datetime.now() + timedelta(+2)).strftime("%Y%m%d")) + ' 17:15:10'
                sleeptime = (datetime.strptime(wakeuptime, "%Y%m%d %H:%M:%S") - datetime.strptime(currtime,
                                                                                                  "%Y%m%d %H:%M:%S")).total_seconds()
                print(params[0], 'sleeping' + "and wakesup at " + wakeuptime)
                time.sleep(sleeptime)
            else:
                if week_day != 4 and "NZD" in params[0]:
                    if "12:59:50" <= currtime[-8:] <= "13:15:05":
                        sleeptime = (
                                datetime.strptime("13:15:10", '%H:%M:%S') - datetime.strptime(currtime[-8:],
                                                                                              '%H:%M:%S')).total_seconds()
                        print(params[0], "sleeping till mkt opens at 13:15")
                        time.sleep(sleeptime)  # sleeptime

                else:
                    if "16:59:50" <= currtime[-8:] <= "17:15:05":
                        sleeptime = (
                                datetime.strptime("17:15:10", '%H:%M:%S') - datetime.strptime(currtime[-8:],
                                                                                              '%H:%M:%S')).total_seconds()
                        print(params[0], "sleeping till mkt opens at 17:15")
                        time.sleep(sleeptime)  # sleeptime

            rt_price = ask_bid(contract, tickerId)
            while rt_price[0] == -1 or rt_price[1] == -1:
                negative_time = datetime.now().strftime("%H:%M:%S")
                print("!!!!!! VALID DATA NOT OBTAINED FROM IB FOR " + params[0] + negative_time + " !!!!")
                print(datetime.now().strftime("%Y%m%d %H:%M:%S"))
                tickerId = random.randint(5000, 8000)
                rt_price = ask_bid(contract, tickerId)
            # tickerId = rt_price[-1]
            if london_list.index(params[0]) <= 4:
                # print("SHORT")
                if condition_buy == "NOT FULFILLED":
                    # print("WAITING TO CROSS", tp_buy)
                    if rt_price[0] <= tp_buy:
                        # print(rt_price[0], tp_buy)
                        signal = "BUY"
                        id = int(ids[1][0])
                        price = float(round(rt_price[0], round1))
                        qty = abs(pos)
                        # print("BUY CONDITION MET")
                        condition1 = "MET"
                else:
                    # print("EXIT CRITERIA MET")
                    condition1 = "MET ALREADY"
            elif london_list.index(params[0]) == 5:
                # print("LONG")
                if condition_sell == "NOT FULFILLED":
                    # print("WAITING TO CROSS", tp_sell)
                    if rt_price[1] >= tp_sell:
                        # print(rt_price[1], tp_sell)
                        signal = "SELL"
                        id = int(ids[0][0])
                        price = float(round(rt_price[1], round1))
                        qty = abs(pos)
                        # print("SELL CONDITION MET")
                        condition1 = "MET"
                else:
                    # print("EXIT CRITERIA MET")
                    condition1 = "MET ALREADY"

            elif london_list.index(params[0]) > 5:

                london_log=pd.read_csv("E:/log_london.csv")
                trade1 = london_log.loc[london_log.CURRENCY == params[0], "SELL_QTY"].iloc[-1]
                trade2 = london_log.loc[london_log.CURRENCY == params[0], "BUY_QTY"].iloc[-1]

                if rt_price[0] <= tp_buy:

                    if condition_buy == "NOT FULFILLED" and trade2 > 0:
                        # print(rt_price[0], tp_buy)
                        signal = "BUY"
                        print(signal, condition_buy)
                        id = int(ids[1][0])
                        # print("ID IS,", id)
                        price = float(round(rt_price[0], round1))

                        if pos > 0:
                            qty = abs(remainqty) + abs(buy_qty)
                        else:
                            qty = abs(buy_qty)
                        print("SENDING", signal, qty)

                        condition1 = "MET"
                    else:

                        condition1 = "MET ALREADY"

                if rt_price[1] >= tp_sell:
                    if condition_sell == "NOT FULFILLED" and trade1 > 0:
                        signal = "SELL"
                        print(signal, condition_sell)
                        id = int(ids[0][0])

                        price = float(round(rt_price[1], round1))

                        if pos < 0:
                            qty = abs(remainqty) + abs(sell_qty)
                        else:
                            qty = abs(sell_qty)
                        print("SENDING", signal, qty)
                        condition1 = "MET"
                    else:

                        condition1 = "MET ALREADY"
                    #########MAIN CONDITION FOR EXIT EXECUTION###################################################################
            if condition1 == "MET":
                # id = transmit_exit(contract, qty, signal, price)  ### to be removed
                # print("ORDER EXPIRY:", exp_date1)
                order_info = create.create_order(acc, "LMT", int(qty), signal, float(price), True, 'GTD', exp_date1)
                tws.placeOrder(id, contract, order_info)
                time.sleep(1)
                confirm = pd.DataFrame()
                while confirm.empty:
                    confirm_data = list(callback.order_Status)
                    for j in range(0, len(confirm_data)):
                        confirm_data[j] = tuple(confirm_data[j])
                    confirm = pd.DataFrame(confirm_data,
                                           columns=['orderId', 'status', 'filled', 'remaining', 'avgFillPrice'
                                               , 'permId', 'parentId', 'lastFillPrice', 'clientId', 'whyHeld'])
                if confirm[confirm.orderId == id].empty == False:
                    status = confirm[confirm.orderId == id].tail(1).iloc[0]['status']
                    remain = confirm[confirm.orderId == id].tail(1).iloc[0]['remaining']
                    filled = confirm[confirm.orderId == id].tail(1).iloc[0]['filled']

                    if remain > 0:
                        partial_fill = int(filled)
                        remain_qty = int(remain)
                        exit_exeprice = 0
                        round1 = 5
                        if signal == "BUY":
                            tp_buy = tp_buy2
                            condition_buy = "NOT FULFILLED"
                        elif signal == "SELL":
                            tp_sell = tp_sell2
                            condition_sell = "NOT FULFILLED"
                    elif remain == 0:
                        exit_exeprice = confirm[confirm.orderId == id].tail(1).iloc[0]['avgFillPrice']
                        exit_exeprice = float(round((exit_exeprice), 4))
                        # print("CONDITION MET,BREAKING ")
                        if signal == "BUY":
                            condition_buy = "FULFILLED"
                            print(signal, condition_buy)
                            exetime = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
                            exit_buy_list = [actual_tp_buy, exit_exeprice, filled, signal, exetime]
                            ### remove from csv the filled curr values
                            london_log = pd.read_csv("E:/log_london.csv")
                            london_log.loc[london_log.CURRENCY == params[0], ["TP_BUY", "BUY_QTY"]] = 0, 0
                            london_log.to_csv("E:/log_london.csv")

                        elif signal == "SELL":
                            condition_sell = "FULFILLED"
                            exetime = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
                            exit_sell_list = [actual_tp_sell, exit_exeprice, filled, signal, exetime]
                            ### remove from csv the filled curr values
                            london_log = pd.read_csv("E:/log_london.csv")
                            london_log.loc[london_log.CURRENCY == params[0], ["TP_SELL", "SELL_QTY"]] = 0, 0
                            london_log.to_csv("E:/log_london.csv")

            dat = open_pos()
            if (dat.empty) or (dat[(dat["Local Symbol"] == params[0])].empty) or (
                    int(dat[(dat["Local Symbol"] == params[0])].iloc[-1]['Position']) == 0):
                # print(pos)
                pos = 0

            # else:
            #     pos = int(dat[(dat["Local Symbol"] == params[0])].iloc[-1]['Position'])
            #     print(pos)
            ##here
            check_time = datetime.now().strftime("%Y%m%d %H:%M:%S")

            # if check_time >= "20180214 15:30:00":
            if check_time >= exp_date1:
                exit_buy_list = [actual_tp_buy, "null", "null", "null", "null"]
                exit_sell_list = [actual_tp_sell, "null", "null", "null", "null"]

                break

            # check_time = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
            # if check_time>=exp_date1:
            #     break

    list1 = [params[0], exit_buy_list, exit_sell_list]
    print(list1)
    print("END OF TRADE")




def run_london():
    disconn()
    conn()


    #### read the csv that has the existing tp values from the original code



    df_london=pd.read_csv("E:/log_london.csv")


    id_list = [[0], [0]]
    params=["AUD.NZD"]
    contract = create.create_contract(params[0][0:3], "CASH", "IDEALPRO", params[0][4:7], '', '', '','')
    ids1=orderidfun(acc,contract,"BUY",id_list,2)
    id_list=ids1

    params = ["CHF.NOK"]
    contract = create.create_contract(params[0][0:3], "CASH", "IDEALPRO", params[0][4:7], '', '', '', '')
    ids2 = orderidfun(acc, contract, "BUY", id_list, 2)
    id_list = ids2

    params = ["CHF.SEK"]
    contract = create.create_contract(params[0][0:3], "CASH", "IDEALPRO", params[0][4:7], '', '', '', '')
    ids3 = orderidfun(acc, contract, "BUY", id_list, 2)
    id_list = ids3

    params = ["NZD.CHF"]
    contract = create.create_contract(params[0][0:3], "CASH", "IDEALPRO", params[0][4:7], '', '', '', '')
    ids4 = orderidfun(acc, contract, "BUY", id_list, 2)
    id_list = ids4

    params = ["GBP.SEK"]
    contract = create.create_contract(params[0][0:3], "CASH", "IDEALPRO", params[0][4:7], '', '', '', '')
    ids5 = orderidfun(acc, contract, "BUY", id_list, 2)
    id_list = ids5

    params = ["EUR.NZD"]
    contract = create.create_contract(params[0][0:3], "CASH", "IDEALPRO", params[0][4:7], '', '', '', '')
    ids6 = orderidfun(acc, contract, "BUY", id_list, 2)
    id_list = ids6

    params = ["EUR.NOK"]
    contract = create.create_contract(params[0][0:3], "CASH", "IDEALPRO", params[0][4:7], '', '', '', '')
    ids7 = orderidfun(acc, contract, "BUY", id_list, 2)
    id_list = ids7

    params = ["EUR.SEK"]
    contract = create.create_contract(params[0][0:3], "CASH", "IDEALPRO", params[0][4:7], '', '', '', '')
    ids8 = orderidfun(acc, contract, "BUY", id_list, 2)
    id_list = ids8

    params = ["GBP.NOK"]
    contract = create.create_contract(params[0][0:3], "CASH", "IDEALPRO", params[0][4:7], '', '', '', '')
    ids9 = orderidfun(acc, contract, "BUY", id_list, 2)
    id_list = ids9

    params = ["NOK.SEK"]
    contract = create.create_contract(params[0][0:3], "CASH", "IDEALPRO", params[0][4:7], '', '', '', '')
    ids10 = orderidfun(acc, contract, "BUY", id_list, 2)
    id_list = ids10

    london_log = pd.read_csv("E:/log_london.csv")
    df_switch = pd.read_excel('E:/database/FX_DAILY/FOREX_settings.xlsx', 'LONDON_SWITCH')
    switchflag = df_switch.loc[df_switch.CURRENCY == 'AUD.NZD', 'TRADE'].iloc[-1]
    if (0 <= df_switch.loc[df_switch.CURRENCY == 'AUD.NZD', 'TP1'].iloc[-1] <= 0.25) and \
            (0 <= df_switch.loc[df_switch.CURRENCY == 'AUD.NZD', 'TP2'].iloc[-1] <= 0.25) and (switchflag in ('yes', 'YES')):

        trade=int(london_log.loc[london_log.CURRENCY=="AUD.NZD","BUY_QTY"].iloc[-1])
        if trade > 0:
            Thread(target=LONDON, args=(["AUD.NZD"], ids1, 100)).start()
        else:
            print("AUD.NZD EXECUTED ALREADY")
    ################################################
    switchflag1 = df_switch.loc[df_switch.CURRENCY == 'CHF.NOK', 'TRADE'].iloc[-1]
    if (0 <= df_switch.loc[df_switch.CURRENCY == 'CHF.NOK', 'TP1'].iloc[-1] <= 0.25) and \
            (0 <= df_switch.loc[df_switch.CURRENCY == 'CHF.NOK', 'TP2'].iloc[-1] <= 0.25) and (
            switchflag1 in ('yes', 'YES')):

        trade = london_log.loc[london_log.CURRENCY == "CHF.NOK", "BUY_QTY"].iloc[-1]
        if trade > 0:
            Thread(target=LONDON, args=(["CHF.NOK"], ids2, 300)).start()
        else:
            print("CHF.NOK EXECUTED ALREADY")

    ###############################################
    switchflag2 = df_switch.loc[df_switch.CURRENCY == 'CHF.SEK', 'TRADE'].iloc[-1]
    if (0 <= df_switch.loc[df_switch.CURRENCY == 'CHF.SEK', 'TP1'].iloc[-1] <= 0.25) and \
            (0 <= df_switch.loc[df_switch.CURRENCY == 'CHF.SEK', 'TP2'].iloc[-1] <= 0.25) and (
            switchflag2 in ('yes', 'YES')):

        trade = london_log.loc[london_log.CURRENCY == "CHF.SEK", "BUY_QTY"].iloc[-1]
        if trade > 0:
            Thread(target=LONDON, args=(["CHF.SEK"], ids3, 500)).start()
        else:
            print("CHF.SEK EXECUTED ALREADY")

    ##########################################################
    switchflag3 = df_switch.loc[df_switch.CURRENCY == 'NZD.CHF', 'TRADE'].iloc[-1]
    if (0 <= df_switch.loc[df_switch.CURRENCY == 'NZD.CHF', 'TP1'].iloc[-1] <= 0.25) and \
            (0 <= df_switch.loc[df_switch.CURRENCY == 'NZD.CHF', 'TP2'].iloc[-1] <= 0.25) and (
            switchflag3 in ('yes', 'YES')):
        trade = london_log.loc[london_log.CURRENCY == "NZD.CHF", "BUY_QTY"].iloc[-1]
        if trade > 0:
            Thread(target=LONDON, args=(["NZD.CHF"], ids4, 700)).start()
        else:
            print("NZD.CHF EXECUTED ALREADY")


    ############################################################################
    switchflag4 = df_switch.loc[df_switch.CURRENCY == 'GBP.SEK', 'TRADE'].iloc[-1]
    if (0 <= df_switch.loc[df_switch.CURRENCY == 'GBP.SEK', 'TP1'].iloc[-1] <= 0.25) and \
            (0 <= df_switch.loc[df_switch.CURRENCY == 'GBP.SEK', 'TP2'].iloc[-1] <= 0.25) and (
            switchflag4 in ('yes', 'YES')):
        trade = london_log.loc[london_log.CURRENCY == "GBP.SEK", "BUY_QTY"].iloc[-1]
        if trade > 0:
            Thread(target=LONDON, args=(["GBP.SEK"], ids5, 900)).start()
        else:
            print("GBP.SEK EXECUTED ALREADY")

    ###############################################################

    switchflag5 = df_switch.loc[df_switch.CURRENCY == 'EUR.NZD', 'TRADE'].iloc[-1]
    if (0 <= df_switch.loc[df_switch.CURRENCY == 'EUR.NZD', 'TP1'].iloc[-1] <= 0.25) and \
            (0 <= df_switch.loc[df_switch.CURRENCY == 'EUR.NZD', 'TP2'].iloc[-1] <= 0.25) and (
            switchflag5 in ('yes', 'YES')):
        trade = london_log.loc[london_log.CURRENCY == "EUR.NZD", "SELL_QTY"].iloc[-1]
        if trade > 0:
            Thread(target=LONDON, args=(["EUR.NZD"], ids6, 1100)).start()
        else:
            print("EUR.NZD EXECUTED ALREADY")


    ###########################################################################

    switchflag6 = df_switch.loc[df_switch.CURRENCY == 'EUR.NOK', 'TRADE'].iloc[-1]
    if (0 <= df_switch.loc[df_switch.CURRENCY == 'EUR.NOK', 'TP1'].iloc[-1] <= 0.25) and \
            (0 <= df_switch.loc[df_switch.CURRENCY == 'EUR.NOK', 'TP2'].iloc[-1] <= 0.25) and (
            switchflag6 in ('yes', 'YES')):
        trade1 = london_log.loc[london_log.CURRENCY == "EUR.NOK", "SELL_QTY"].iloc[-1]
        trade2 = london_log.loc[london_log.CURRENCY == "EUR.NOK", "BUY_QTY"].iloc[-1]
        if trade1 > 0 or trade2 > 0:
            Thread(target=LONDON, args=(["EUR.NOK"], ids7, 1200)).start()
        else:
            print("EUR.NOK EXECUTED ALREADY")


    ##############################################

    switchflag7 = df_switch.loc[df_switch.CURRENCY == 'EUR.SEK', 'TRADE'].iloc[-1]
    if (0 <= df_switch.loc[df_switch.CURRENCY == 'EUR.SEK', 'TP1'].iloc[-1] <= 0.25) and \
            (0 <= df_switch.loc[df_switch.CURRENCY == 'EUR.SEK', 'TP2'].iloc[-1] <= 0.25) and (
            switchflag7 in ('yes', 'YES')):
        trade1 = london_log.loc[london_log.CURRENCY == "EUR.SEK", "SELL_QTY"].iloc[-1]
        trade2 = london_log.loc[london_log.CURRENCY == "EUR.SEK", "BUY_QTY"].iloc[-1]
        if trade1 > 0 or trade2 > 0:
            Thread(target=LONDON, args=(["EUR.SEK"], ids8, 1400)).start()
        else:
            print("EUR.SEK EXECUTED ALREADY")

    ##################################################################
    switchflag8 = df_switch.loc[df_switch.CURRENCY == 'GBP.NOK', 'TRADE'].iloc[-1]
    if (0 <= df_switch.loc[df_switch.CURRENCY == 'GBP.NOK', 'TP1'].iloc[-1] <= 0.25) and \
            (0 <= df_switch.loc[df_switch.CURRENCY == 'GBP.NOK', 'TP2'].iloc[-1] <= 0.25) and (
            switchflag8 in ('yes', 'YES')):
        trade1 = london_log.loc[london_log.CURRENCY == "GBP.NOK", "SELL_QTY"].iloc[-1]
        trade2 = london_log.loc[london_log.CURRENCY == "GBP.NOK", "BUY_QTY"].iloc[-1]
        if trade1 > 0 or trade2 > 0:
            Thread(target=LONDON, args=(["GBP.NOK"], ids9, 1600)).start()
        else:
            print("GBP.NOK EXECUTED ALREADY")



    ##########################################################
    switchflag9 = df_switch.loc[df_switch.CURRENCY == 'NOK.SEK', 'TRADE'].iloc[-1]
    if (0 <= df_switch.loc[df_switch.CURRENCY == 'NOK.SEK', 'TP1'].iloc[-1] <= 0.25) and \
            (0 <= df_switch.loc[df_switch.CURRENCY == 'NOK.SEK', 'TP2'].iloc[-1] <= 0.25) and (
            switchflag9 in ('yes', 'YES')):
        trade1 = london_log.loc[london_log.CURRENCY == "NOK.SEK", "SELL_QTY"].iloc[-1]
        trade2 = london_log.loc[london_log.CURRENCY == "NOK.SEK", "BUY_QTY"].iloc[-1]
        if trade1 > 0 or trade2 > 0:
            Thread(target=LONDON, args=(["NOK.SEK"], ids10, 1800)).start()
        else:
            print("NOK.SEK EXECUTED ALREADY")



    return

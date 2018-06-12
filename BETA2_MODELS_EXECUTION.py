############################# PACKAGES ##################################################
import numpy as np
import math
import time
import timeit
import random
from IBWrapper import IBWrapper, contract
from ib.ext.EClientSocket import EClientSocket
import time
import csv
import timeit
import random
import pandas as pd
from datetime import datetime, timedelta

################## global declarations ########################################

## ________________________ CONNECTIVITY  _______________________________________________________________##
callback = IBWrapper()
tws = EClientSocket(callback)
host = ""
port = 7497
clientId = 100
create = contract()
callback.initiate_variables()
tws.reqGlobalCancel()


##decimal fn to alter price
def decimal(f, n):
    return math.floor(f * 10 ** n) / 10 ** n


def conn():
    status = tws.isConnected()
    if status == False:
        print("######### $$$$$$$$$$$$$$$$$$ RECONNECTING TWS SESSION   $$$$$$$$$$$$$$$$$$############")
        tws.eConnect(host, port, clientId)
        print("######### $$$$$$$$$$$$$$$$$$$ TWS CONNECTED   $$$$$$$$$$$$$$$$$$############")
    else:
        print("######### $$$$$$$$$$$$$$$$$$$ TWS CONNECTION INTACT  $$$$$$$$$$$$$$$$$$############")
    return


conn()


def disconn():
    tws.eDisconnect()
    print("######### $$$$$$$$$$$$$$$$$$$ TWS DISCONNECTED   $$$$$$$$$$$$$$$$$$############")
    return


##_______________________________  REAL TIME DATA OF CONTRACT ____________________________________________##
def tickerId():
    a = random.sample(range(60001, 60900), 40)
    b = random.sample(range(60901, 70600), 40)
    random.shuffle(a)
    random.shuffle(b)
    tickerId = a[0] + b[0]
    return tickerId


def realtime(tickerid, contract_Details):
    data = pd.DataFrame()
    while data.empty:
        tickerId = tickerid
        # print(datetime.now())
        tws.reqRealTimeBars(tickerId,
                            contract_Details,
                            5,
                            "TRADES",  ##### ---------------- ALTERNATE PARAMETERS- MIDPOINT/ASK/BID  ----------------
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
    data = data['close'].iloc[-1]
    return data


def ask_bid(contract, tickerId):
    tickedId = int(tickerId)

    tick = contract

    ask = 1
    bid = 1
    last = 1
    from numbers import Number

    # while not isinstance(ask,float) and not isinstance(bid,float):
    while ask == 1 and bid == 1 and last == 1:
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
        # print(tick_data1)
        a = tick_data1
        # print(a)
        status1 = 'ASK PRICE' in tick_data1.Type.values
        status2 = 'BID PRICE' in tick_data1.Type.values
        status3 = "LAST PRICE" in tick_data1.Type.values
        time.sleep(1)
        print("ASK", status1, "BID", status2)
        if status1 == False or status2 == False or status3 == False:
            print("ASK AND BID UNAVAILABLE FOR")
            ask = 1
            bid = 1
            last = 1
        else:
            print("ASK AND BID AVAILABLE")
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

    print("OBTAINED CORRECT DETAILS FOR")
    return ask, bid, last



####_________________________HISTORICAL REQ____________________________________________________________##

def historical(fortime, con, totaldays):
    date = datetime.now()
    date = date.strftime('%Y%m%d') + fortime
    df = pd.DataFrame()
    while df.empty:
        a = random.sample(range(901, 1200), 1)
        b = random.sample(range(1201, 1500), 1)
        random.shuffle(a)
        random.shuffle(b)
        Id1 = a[0] + b[0]
        tws.reqHistoricalData(Id1, con, date,
                              totaldays,
                              '1 day',
                              "TRADES",
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

        df = df[0:-1]
        # df=df.tail(31)
    return df


total_cap = 2000000
Core_port_levrg = 1
LDN_curr_levrg = 16
NY_curr_levrg = 5

transformation_1_wghts = 0.03816
transformation_2_wghts = 0.03669
metaphor_wghts = 0.06162
camouflage_wghts = 0.20775
fundamentals_wghts = 0.06747

camouflage_intraday_TP = 0.05
camouflage_EOD_TP = 0.03

transformation_1 = 'YES'
transformation_2 = 'YES'
metaphor = 'YES'
camouflage = 'YES'
fundamentals = 'YES'
hl_eqty = 'YES'
hl_curr_ldn = 'YES'
hl_curr_ny = 'YES'

##########################################################################

core_port_cap = total_cap * Core_port_levrg
ldn_curr_port_cap = total_cap * LDN_curr_levrg
ny_curr_port_cap = total_cap * NY_curr_levrg

transformation_1_cap_usd = transformation_1_wghts * core_port_cap
transformation_2_cap_usd = transformation_2_wghts * core_port_cap
metaphor_cap_usd = metaphor_wghts * core_port_cap
NG_cap_usd = camouflage_wghts * core_port_cap
fundamentals_cap_usd = fundamentals_wghts * core_port_cap
DAX_cap_usd = 0.0662 * core_port_cap
ESTX_50_cap_usd = 0.022207 * core_port_cap








def contract1(sym, sec, exc, curr, blank, blank2, expiry, mul):
    contract_Details = create.create_contract(sym, sec, exc, curr, blank, blank2, expiry, mul)
    return contract_Details

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

def orderidfun(acc,order_params,exitidlist):

    time.sleep(5)
    loops = 7
    contract_info = order_params[3]
    asset_type = order_params[1]
    asset_name = order_params[0]
    if asset_type == 'LONG':
        exit_signal = 'SELL'
    elif asset_type == 'SHORT':
        exit_signal = 'BUY'

    sellidlist = generateNumber(loops)


    exitidlist=[0]
    while sellidlist[0] == exitidlist:
        sellidlist = generateNumber(loops)
    for i in sellidlist:
        order_info = create.create_order(acc, "LMT", 10000, "SELL", 10.00, False, False, None)
        tws.placeOrder(int(i), contract_info, order_info)

    buyidlist = generateNumber(loops)

    while buyidlist[0] == sellidlist[0]:
        buyidlist = generateNumber(loops)

    for i in buyidlist:
        order_info = create.create_order(acc, "LMT", 10000, "BUY", 10.00, False, False, None)
        tws.placeOrder(int(i), contract_info, order_info)

    loops = 1
    exitidlist = generateNumber(loops)

    while exitidlist[0] == buyidlist[0]:
        exitidlist = generateNumber(loops)

    for i in exitidlist:
        order_info = create.create_order(acc, "LMT", 10000, exit_signal, 10.00, False, False, None)
        tws.placeOrder(int(i), contract_info, order_info)

    print(asset_name,"SELL GTD:",sellidlist)
    print(asset_name,"BUY GTD:", buyidlist)
    print(asset_name,"EXIT ID:", exitidlist)

    return sellidlist,buyidlist,exitidlist

def push_order(signal,qty,sell_list,buy_list):
    #### TRY 6 TIMES MAX TO PLACE THE ENTRY ####
    order_id1=0

    camouflage_sig=signal
    camouflage_qty=qty
    ng_sell_list=sell_list
    ng_buy_list=buy_list

    camouflage_price=0
    exp_date="null"

    order_info = create.create_order(acc, "LMT", camouflage_qty, camouflage_sig, camouflage_price, True, 'GTD',
                                     exp_date)
    for i in range(6):
        a = random.sample(range(1, 300), 1)
        b = random.sample(range(301, 600), 1)
        random.shuffle(a)
        random.shuffle(b)

        tickerId1 = a[0] + b[0]

        ## get ask and bid to place order ##


        signal_price = ask_bid(ng_contract, tickerId1)

        ## set GTD duration ##
        exp_date = datetime.now() + timedelta(seconds=+25)
        exp_date = exp_date.strftime('%Y%m%d %H:%M:%S')

        if camouflage_sig == 'SELL':
            camouflage_qty = int(camouflage_qty)
            camouflage_price = float(signal_price[0])
            print(camouflage_price)
            order_info = create.create_order(acc, "LMT", camouflage_qty, camouflage_sig, camouflage_price, True, 'GTD',
                                             exp_date)
            order_id1 = int(ng_sell_list[0])
            ##############to cancel#################
            ng_sell_list.remove(ng_sell_list[0])

        elif camouflage_sig == 'BUY':
            camouflage_qty = int(camouflage_qty)
            camouflage_price = float(signal_price[1])
            print(camouflage_price)
            order_info = create.create_order(acc, "LMT", camouflage_qty, camouflage_sig, camouflage_price, True, 'GTD',
                                             exp_date)
            ################to cancel
            order_id1 = int(ng_buy_list[0])
            ng_buy_list.remove(ng_buy_list[0])

        tws.placeOrder(order_id1, ng_contract, order_info)
        ##########new condition################
        time.sleep(28)
        confirm = pd.DataFrame()
        while confirm.empty:
            confirm_data = list(callback.order_Status)
            for j in range(0, len(confirm_data)):
                confirm_data[j] = tuple(confirm_data[j])
            confirm = pd.DataFrame(confirm_data,
                                   columns=['orderId', 'status', 'filled', 'remaining', 'avgFillPrice',
                                            'permId', 'parentId', 'lastFillPrice', 'clientId', 'whyHeld'])

        if confirm[confirm.orderId == order_id1].empty == False:

            status = confirm[confirm.orderId == order_id1].tail(1).iloc[0]['status']
            remain = confirm[confirm.orderId == order_id1].tail(1).iloc[0]['remaining']
            if remain > 0:

                ng_remain_qty = int(remain)
                print("not filled")
                # time.sleep(1)
            elif remain == 0:
                exeprice = confirm[confirm.orderId == order_id1].tail(1).iloc[0]['avgFillPrice']

        ####### runs 6 times untill gtd is placed ######
        ####breaks out of function once entry placed ######
        break

        ##############check if gtd  trade got executed#########################
    for i in range(0, 5):
        tws.reqPositions()
        dat1 = list(callback.update_Position)
        if len(dat1) == 0:
            print("empty dat1")
            dat1 = pd.DataFrame()
            # time.sleep(30-15*i)
            time.sleep(0.5)

        else:
            for k in range(0, len(dat1)):
                dat1[k] = tuple(dat1[k])
            dat1 = pd.DataFrame.from_records(dat1,
                                             columns=['Account', 'Contract ID', 'Currency', 'Exchange',
                                                      'Expiry',
                                                      'Include Expired', 'Local Symbol', 'Multiplier', 'Right',
                                                      'Security Type', 'Strike', 'Symbol', 'Trading Class',
                                                      'Position', 'Average Cost'])

            dat1[dat1["Account"] == 'DU536394']
            break
    ng_remain_qty=0
    if (dat1[(dat1["Symbol"] == "NG")].empty) or (
                abs(int(dat1[(dat1["Symbol"] == "NG")].iloc[-1]['Position'])) != camouflage_qty):
        print('GTD not filled, placing lmt order')

        a = random.sample(range(1, 300), 1)
        b = random.sample(range(301, 600), 1)
        random.shuffle(a)
        random.shuffle(b)

        tickerId2 = tickerId()
        ng_rt = ask_bid(ng_contract, tickerId2)

        ###########placing order#####################################

        if camouflage_sig == 'SELL':

            entryprice = float(ng_rt[0])
            print(entryprice)

            order_info = create.create_order(acc, "LMT", int(ng_remain_qty), camouflage_sig, entryprice, True, False,
                                             None)

            lmtorder_id1 = int(ng_sell_list[0])
            ############to cancel############
            ng_sell_list.remove(ng_sell_list[0])

        elif camouflage_sig == 'BUY':

            entryprice = float(ng_rt[1])
            print(entryprice)

            order_info = create.create_order(acc, "LMT", int(ng_remain_qty), camouflage_sig, entryprice, True, False,
                                             None)
            lmtorder_id1 = int(ng_buy_list[0])
            ##############to cancel####################
            ng_buy_list.remove(ng_buy_list[0])

        tws.placeOrder(lmtorder_id1, ng_contract, order_info)

        time.sleep(5)
        ################################################checking for status##############

        while True:
            confirm = pd.DataFrame()
            while confirm.empty:
                confirm_data = list(callback.order_Status)
                for j in range(0, len(confirm_data)):
                    confirm_data[j] = tuple(confirm_data[j])
                confirm = pd.DataFrame(confirm_data,
                                       columns=['orderId', 'status', 'filled', 'remaining', 'avgFillPrice',
                                                'permId', 'parentId', 'lastFillPrice', 'clientId', 'whyHeld'])

            status = confirm[confirm.orderId == lmtorder_id1].tail(1).iloc[0]['status']
            filledqty = confirm[confirm.orderId == lmtorder_id1].tail(1).iloc[0]['filled']
            if status == 'Filled':
                exeprice = confirm[confirm.orderId == lmtorder_id1].tail(1).iloc[0]['avgFillPrice']
                # position = ng_remain_qty
                break

            elif status == 'Submitted':
                time.sleep(5)
    qty=camouflage_qty+ng_remain_qty
    return exeprice,qty,camouflage_sig

sec = "FUT"
curr = "USD"
blank = ''
blank2 = ''
acc = 'DU228380'

camouflage_list1 = ["NG", "NYMEX", '20180518', '10000']  # used for pulling data from IB
camouflage_list2 = ["CL", "NYMEX", '20180122', '1000']  # used for pulling data from IB
camouflage_list3 = [' 19:35:00', '5 D']  # strategy specific details
ng_contract = contract1(camouflage_list1[0], sec, camouflage_list1[1], curr, blank, blank2, camouflage_list1[2],
                        camouflage_list1[3])
crude_contract = contract1(camouflage_list2[0], sec, camouflage_list2[1], curr, blank, blank2, camouflage_list2[2],
                           camouflage_list2[3])
ng_params=[camouflage_list1[0],"LONG","",ng_contract]



def ng_main():
    sec = "FUT"
    curr = "USD"
    blank = ''
    blank2 = ''
    acc = 'DU228380'

    camouflage_list1 = ["NG", "NYMEX", '20180129', '10000']  # used for pulling data from IB
    camouflage_list2 = ["CL", "NYMEX", '20180122', '1000']  # used for pulling data from IB
    camouflage_list3 = [' 19:35:00', '5 D']  # strategy specific details
    ng_contract = contract1(camouflage_list1[0], sec, camouflage_list1[1], curr, blank, blank2, camouflage_list1[2],
                            camouflage_list1[3])
    crude_contract = contract1(camouflage_list2[0], sec, camouflage_list2[1], curr, blank, blank2, camouflage_list2[2],
                               camouflage_list2[3])


    ng_params=[camouflage_list1[0],"LONG","",ng_contract]
    exitidlist=[]
    idlist=orderidfun(acc,ng_params,exitidlist)
    ng_sell_id=idlist[0]
    ng_buy_id=idlist[1]

    ## historical data
    ng_hist = historical(camouflage_list3[0], ng_contract, camouflage_list3[1])
    cl_hist = historical(camouflage_list3[0], crude_contract, camouflage_list3[1])

    ## real time ask, bid and last price

    ng_id = tickerId()
    cl_id = tickerId()
    ng_rt = ask_bid(ng_contract, ng_id)
    cl_rt = ask_bid(crude_contract, cl_id)

    camouflage_qty = 0
    opensignal = "NONE"
    camouflage_sig = 'NO SIG'

    ##############################################################################
    # get the signals using the strategy logic and store in "camouflage_sig" variable

    if (cl_rt[2] > cl_hist.iloc[0]['close'] and ng_rt[2] < ng_hist.iloc[0]['close']):
        camouflage_sig = 'BUY'
        camouflage_qty = max((int(math.ceil((((NG_cap_usd / (ng_rt[1] * int(camouflage_list1[3]))) / 10000) * 10000))), 1))
        # entry_date=datetime.now().date()
    elif (cl_rt[2] < cl_hist.iloc[0]['close'] and ng_rt[2] > ng_hist.iloc[0]['close']):
        camouflage_sig = 'SELL'
        camouflage_qty = max((int(math.ceil((((NG_cap_usd / (ng_rt[0] * int(camouflage_list1[3]))) / 10000) * 10000))), 1))
        # entry_date = datetime.now().date()
    else:
        camouflage_sig = 'NO SIG'

    #################################################################################
    if (camouflage_sig != 'NO SIG'):
        for i in range(0, 5):
            tws.reqPositions()
            mdat = list(callback.update_Position)
            if len(mdat) == 0:
                print("empty mdat")
                mdat = pd.DataFrame()
                # time.sleep(30-15*i)
                time.sleep(0.5)

            else:
                for k in range(0, len(mdat)):
                    mdat[k] = tuple(mdat[k])
                mdat = pd.DataFrame.from_records(mdat,
                                                  columns=['Account', 'Contract ID', 'Currency', 'Exchange', 'Expiry',
                                                           'Include Expired', 'Local Symbol', 'Multiplier', 'Right',
                                                           'Security Type', 'Strike', 'Symbol', 'Trading Class',
                                                           'Position', 'Average Cost'])

                mdat[mdat["Account"] == 'DU536394']
                break
        if (mdat.empty) or (mdat[(mdat["Symbol"] == "NG")].empty) or (
            int(mdat[(mdat["Symbol"] == "NG")].iloc[-1]['Position']) == 0):
            print("NO OPEN POSITION & NO NEW ENTRY SIGNAL")
        else:
            openpos = int(mdat[(mdat["Symbol"] == "NG")].iloc[-1]['Position'])
            if openpos > 0:
                opensignal = "BUY"
                exitsignal = "SELL"
                exit_price = ng_rt[0]
                diff_price = ng_rt[1]
            elif openpos < 0:
                opensignal = "SELL"
                exitsignal = "BUY"
                exit_price = ng_rt[1]
                diff_price = ng_rt[0]
            print("There is an open Position:", openpos, opensignal)
            ng_price = pd.read_csv('C:/Users\RD GR\Desktop/testing/NG_DATA.csv')
            entry_date = ng_price["ENTRY_DATE"].iloc[-1]
            if (np.busday_count(entry_date, datetime.now().date()) >= 5):

                signal=exitsignal
                qty=openpos
                df_params=push_order(signal,qty,ng_sell_id,ng_buy_id)
                print(df_params)

                # order_info = create.create_order(acc, "LMT", openpos, exitsignal, exit_price, True, False, None)
                # tws.placeOrder(int(i), ng_contract, order_info)  ### generate order id fn
            else:
                ng_price = pd.read_csv('C:/Users\RD GR\Desktop/testing/NG_DATA.csv')
                ng_entry_price = float(round(ng_price["ENTRY_PRICE"].iloc[-1], 3))
                if abs((exit_price / ng_entry_price - 1)) >= camouflage_EOD_TP:
                    signal = exitsignal
                    qty = openpos
                    df_params = push_order(signal, qty, ng_sell_id, ng_buy_id)
                    print(df_params)

                    # order_info = create.create_order(acc, "LMT", openpos, exitsignal, exit_price, True, False, None)
                    # tws.placeOrder(int(i), ng_contract, order_info)
    else:
        if camouflage_sig == "SELL":
            camouflage_price = ng_rt[0]  # storing the best sell price (ask)
        else:
            camouflage_price = ng_rt[1]  # storing the best buy price  (bid)
        ### send entry signal ###
        for i in range(0, 5):
            tws.reqPositions()
            mdat = list(callback.update_Position)
            if len(mdat) == 0:
                print("empty mdat")
                mdat = pd.DataFrame()
                # time.sleep(30-15*i)
                time.sleep(0.5)

            else:
                for k in range(0, len(mdat)):
                    mdat[k] = tuple(mdat[k])
                mdat = pd.DataFrame.from_records(mdat,
                                                  columns=['Account', 'Contract ID', 'Currency', 'Exchange', 'Expiry',
                                                           'Include Expired', 'Local Symbol', 'Multiplier', 'Right',
                                                           'Security Type', 'Strike', 'Symbol', 'Trading Class',
                                                           'Position', 'Average Cost'])

                mdat[mdat["Account"] == 'DU536394']
                break
        if (mdat.empty) or (mdat[(mdat["Symbol"] == "NG")].empty) or (
            int(mdat[(mdat["Symbol"] == "NG")].iloc[-1]['Position']) == 0):
            print("NO OPEN POSITION & NEW ENTRY SIGNAL=", camouflage_sig, "QTY=", camouflage_qty)
            ###  PUSHING NEW ENTRY WHEN NO EXISTING POSITIONS##

            signal = camouflage_sig
            qty = camouflage_qty
            df_params = push_order(signal, qty, ng_sell_id, ng_buy_id)
            print(df_params)

            # order_info = create.create_order(acc, "LMT", camouflage_qty, camouflage_sig, camouflage_price, True, False,
            #                                  None)
            # tws.placeOrder(int(i), ng_contract, order_info)  ### generate order id fn
            entry_date = datetime.now().date()
            ng_data = pd.DataFrame(
                {'ENTRY_DATE': [entry_date], 'ENTRY_SIGNAL': [camouflage_sig], 'ENTRY_QTY': [camouflage_qty],
                 'ENTRY_PRICE': [camouflage_price]})
            ng_data.to_csv('C:/Users\RD GR\Desktop/testing/NG_DATA.csv')



        else:
            openpos = int(mdat[(mdat["Symbol"] == "NG")].iloc[-1]['Position'])

            if openpos > 0:
                opensignal = "BUY"
                exitsignal = "SELL"
                exit_price = ng_rt[0]
                diff_price = ng_rt[1]
            elif openpos < 0:
                opensignal = "SELL"
                exitsignal = "BUY"
                exit_price = ng_rt[1]
                diff_price = ng_rt[0]
            print("There is an open Position:", openpos, opensignal)

            ng_data = pd.read_csv('C:/Users\RD GR\Desktop/testing/NG_DATA.csv')
            entry_date = ng_data["ENTRY_DATE"].iloc[-1]
            ng_entry_price = float(round(ng_data["ENTRY_PRICE"].iloc[-1], 3))
            if (np.busday_count(entry_date, datetime.now().date()) >= 5):
                if camouflage_sig == opensignal:
                    if camouflage_qty != openpos:
                        camouflage_diff = abs(camouflage_qty - openpos)

                        signal = camouflage_sig
                        qty = camouflage_diff
                        df_params = push_order(signal, qty, ng_sell_id, ng_buy_id)
                        print(df_params)


                        # order_info = create.create_order(acc, "LMT", camouflage_diff, camouflage_sig, diff_price, True,
                        #                                  False, None)
                        # tws.placeOrder(int(i), ng_contract, order_info)  ### generate order id fn##
                        entry_date = datetime.now().date()
                        ng_data = pd.DataFrame(
                            {'ENTRY_DATE': [entry_date], 'ENTRY_SIGNAL': [camouflage_sig], 'ENTRY_QTY': [camouflage_diff],
                             'ENTRY_PRICE': [diff_price]})
                        ng_data.to_csv('C:/Users\RD GR\Desktop/testing/NG_DATA.csv')
                else:
                    camouflage_qty = abs(camouflage_qty + openpos)

                    signal = camouflage_sig
                    qty = camouflage_qty
                    df_params = push_order(signal, qty, ng_sell_id, ng_buy_id)
                    print(df_params)


                    # order_info = create.create_order(acc, "LMT", camouflage_qty, camouflage_sig, diff_price, True, False,
                    #                                  None)
                    # tws.placeOrder(int(i), ng_contract, order_info)  ### generate order id fn
                    entry_date = datetime.now().date()
                    ng_data = pd.DataFrame(
                        {'ENTRY_DATE': [entry_date], 'ENTRY_SIGNAL': [camouflage_sig], 'ENTRY_QTY': [camouflage_qty],
                         'ENTRY_PRICE': [diff_price]})
                    ng_data.to_csv('C:/Users\RD GR\Desktop/testing/NG_DATA.csv')
            else:
                if abs((exit_price / ng_entry_price - 1)) >= camouflage_EOD_TP:
                    if camouflage_sig == opensignal:
                        if camouflage_qty != openpos:
                            camouflage_diff = abs(camouflage_qty - openpos)

                            signal = camouflage_sig
                            qty = camouflage_diff
                            df_params = push_order(signal, qty, ng_sell_id, ng_buy_id)
                            print(df_params)


                            # order_info = create.create_order(acc, "LMT", camouflage_diff, camouflage_sig, diff_price, True,
                            #                                  False, None)
                            # tws.placeOrder(int(i), ng_contract, order_info)  ### generate order id fn
                            entry_date = datetime.now().date()
                            ng_data = pd.DataFrame({'ENTRY_DATE': [entry_date], 'ENTRY_SIGNAL': [camouflage_sig],
                                                    'ENTRY_QTY': [camouflage_diff], 'ENTRY_PRICE': [diff_price]})
                            ng_data.to_csv('C:/Users\RD GR\Desktop/testing/NG_DATA.csv')
                    else:
                        camouflage_qty = abs(camouflage_qty + openpos)
                        signal = camouflage_sig
                        qty = camouflage_qty
                        df_params = push_order(signal, qty, ng_sell_id, ng_buy_id)
                        print(df_params)

                        # order_info = create.create_order(acc, "LMT", camouflage_qty, camouflage_sig, diff_price, True,
                        #                                  False, None)
                        # tws.placeOrder(int(i), ng_contract, order_info)  ### generate order id fn
                        entry_date = datetime.now().date()
                        ng_data = pd.DataFrame(
                            {'ENTRY_DATE': [entry_date], 'ENTRY_SIGNAL': [camouflage_sig], 'ENTRY_QTY': [camouflage_qty],
                             'ENTRY_PRICE': [exit_price]})
                        ng_data.to_csv('C:/Users\RD GR\Desktop/testing/NG_DATA.csv')


    return



from apscheduler.schedulers.background import BackgroundScheduler
sched = BackgroundScheduler()
sched.start()
job1 = sched.add_job(ng_main, 'cron', day_of_week='0,1,2,3,4', hour=21, minute=36, second=00,misfire_grace_time=40)








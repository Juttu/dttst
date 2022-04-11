import time

import pandas as pd
import requests
import datetime
from threading import Timer
import time
from twilio.rest import Client
from datetime import datetime as date
import math

from smartapi import SmartConnect



user_name = 'd135710'
password = 'Itsmyvsh838+'
api_key= 'PjVObAR5'
feed_token = None
token_map = None



client = Client("ACe1cd9a2445658516046b7aa3ea29594b","efbf213215107c6bd57950d4f88bf1a4")

obj=SmartConnect(api_key=api_key)
data = obj.generateSession(user_name,password)
print(data)
refreshToken= data['data']['refreshToken']


feedToken=obj.getfeedToken()
feed_token=feedToken

print(feed_token)


userProfile= obj.getProfile(refreshToken)
print(userProfile)

url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
d = requests.get(url).json()
global token_df
token_df = pd.DataFrame.from_dict(d)
# token_df.to_csv('file1.csv')
token_df['expiry'] = pd.to_datetime(token_df['expiry'])
token_df = token_df.astype({'strike': float})
token_map = token_df




def place_order(token,symbol,qty,exch_seg,buy_sell,ordertype,price):
                try:
                    orderparams = {
                        "variety": "NORMAL",
                        "tradingsymbol": symbol,
                        "symboltoken": token,
                        "transactiontype": buy_sell,
                        "exchange": exch_seg,
                        "ordertype": ordertype,
                        "producttype": "INTRADAY",
                        "duration": "DAY",
                        "price": price,
                        "squareoff": "0",
                        "stoploss": "0",
                        "quantity": qty
                        }
                    orderId=obj.placeOrder(orderparams)
                    print("The order id is: {}".format(orderId))
                    return orderId
                except Exception as e:
                    print("Order placement failed: {}".format(e.message))


# In[8]:


def getTokenInfo (exch_seg, instrumenttype,symbol,strike_price,pe_ce):
                df = token_map
                strike_price = strike_price*100
                

                if exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
                    return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['strike'] == strike_price)  & (df['symbol'].str.endswith(pe_ce)) & (df['expiry']>= str(datetime.date.today()))].sort_values(by=['expiry'])


# In[9]:


def getpremium (symbol,token,exchange):
                
                ltp = obj.ltpData(exchange,symbol,token)
                Ltp = ltp['data']['ltp']
                return Ltp


# In[10]:


def getday ():
        day=date.today().strftime("%A")
        return day

def absvalue(p):
    val = p
    val2 = math.fmod(val, 100)
    x = val - val2
    abs_val = "{:.0f}".format(x)
    abs_val=int(abs_val)
    return abs_val

def msg(m):
        message=client.messages.create(body=m,from_="whatsapp:+14155238886",to="whatsapp:+916303247774")


peinfo1 = getTokenInfo('NFO','OPTIDX','NIFTY',18550,'PE').iloc[0]
pp=getpremium(peinfo1['symbol'],peinfo1['token'],'NFO')
print(pp)

# a=0
# while True:
#     a=a+2
#     print(a)
#     msg("Hello"+str(a))
#     time.sleep(1)

while True:
            
    now = date.now()
    if now.hour!=9 and now.minute>=30:

        sp=getpremium('BANKNIFTY','26009','NSE')
        asp=absvalue(sp)
        
        
        
        ceinfo = getTokenInfo('NFO','OPTIDX','BANKNIFTY',asp,'CE').iloc[0]
        peinfo = getTokenInfo('NFO','OPTIDX','BANKNIFTY',asp,'PE').iloc[0]
        cp=getpremium(ceinfo['symbol'],ceinfo['token'],'NFO')
        pp=getpremium(peinfo['symbol'],peinfo['token'],'NFO')
        
        
        print(ceinfo,peinfo)
        symbol  = ceinfo['symbol']
        token = ceinfo['token']
        lot = int(ceinfo['lotsize'])

        symbol1  = peinfo['symbol']
        token1 = peinfo['token']
        
        ce_order=place_order(token,symbol,lot,'NFO','SELL','MARKET',0)
        pe_order=place_order(peinfo['token'],peinfo['symbol'],lot,'NFO','SELL','MARKET',0)
        
        print(ce_order,pe_order)
        c=1
        p=1

#         print(ce_order)

        cp_sl=1.2*cp
        cp_tp=0.5*cp
        
        pp_sl=1.2*pp
        pp_tp=0.5*pp
        
        while(c==1 and p==1):
              
            
            now = date.now()

            if getpremium(ceinfo['symbol'],ceinfo['token'],'NFO')>=cp_sl:
                place_order(ceinfo['token'],ceinfo['symbol'],lot,'NFO','BUY','MARKET',0)
                loss_cp=(cp-getpremium(ceinfo['symbol'],ceinfo['token'],'NFO'))*25

                new_pp=getpremium(peinfo['symbol'],peinfo['token'],'NFO')
                c=0
                
            if getpremium(peinfo['symbol'],peinfo['token'],'NFO')>=pp_sl:
                place_order(peinfo['token'],peinfo['symbol'],lot,'NFO','BUY','MARKET',0)
                loss_pp=(pp-getpremium(peinfo['symbol'],peinfo['token'],'NFO'))*25

                new_cp=getpremium(ceinfo['symbol'],ceinfo['token'],'NFO')
                p=0
            if now.hour==15 or getpremium(ceinfo['symbol'],ceinfo['token'],'NFO')<=cp_tp or getpremium(peinfo['symbol'],peinfo['token'],'NFO')<=pp_tp:
                place_order(ceinfo['token'],ceinfo['symbol'],lot,'NFO','BUY','MARKET',0)
                place_order(peinfo['token'],peinfo['symbol'],lot,'NFO','BUY','MARKET',0)
                profit_cp=(cp-getpremium(ceinfo['symbol'],ceinfo['token'],'NFO'))*25
                profit_pp=(pp-getpremium(peinfo['symbol'],peinfo['token'],'NFO'))*25


                c=2
                p=2
                
                print('Total P&L :',profit_cp+profit_pp)



                
                
            else :
                print('Call Premium :',cp_tp,getpremium(ceinfo['symbol'],ceinfo['token'],'NFO'),cp_sl)

                print('Put Premium :',pp_tp,getpremium(peinfo['symbol'],peinfo['token'],'NFO'),pp_sl)
        break
 
            
        
        
    else:
        print("Wait")
        

    
    
if c==0:
    
    print("Call Option Exited")
    
    while True:
        tsl_pp=new_pp*1.2
        ttp_pp=new_pp*0.92
        now = date.now()

        if getpremium(peinfo['symbol'],peinfo['token'],'NFO')<=ttp_pp :
            new_pp=getpremium(peinfo['symbol'],peinfo['token'],'NFO')
            print("PUT New TP,SL :",new_pp*0.92,new_pp,new_pp*1.2)
        if getpremium(peinfo['symbol'],peinfo['token'],'NFO')>=tsl_pp or new_pp<=0.5*pp or now.hour==15:
            pp_amount=(pp-getpremium(peinfo['symbol'],peinfo['token'],'NFO'))*25
            place_order(peinfo['token'],peinfo['symbol'],lot,'NFO','BUY','MARKET',0)
            print('Total P&L :',loss_cp+pp_amount)

            break
            
if p==0:
    
    print("Put Option Exited")

    
    
    while True:
        tsl_cp=new_cp*1.2
        ttp_cp=new_cp*0.92
        now = date.now()

        
        if getpremium(ceinfo['symbol'],ceinfo['token'],'NFO')<=ttp_cp :
            new_cp=getpremium(ceinfo['symbol'],ceinfo['token'],'NFO')
            print("CALL New TP,SL :",new_cp*0.92,new_cp,new_cp*1.2)

        if getpremium(ceinfo['symbol'],ceinfo['token'],'NFO')>=tsl_cp or new_cp<=0.5*cp or now.hour==15 :
            cp_amount=(cp-getpremium(ceinfo['symbol'],ceinfo['token'],'NFO'))*25
            place_order(ceinfo['token'],ceinfo['symbol'],lot,'NFO','BUY','MARKET',0)
            print('Total P&L :',loss_pp+cp_amount)
            
            break
        
        

            
            
        
        
        
        


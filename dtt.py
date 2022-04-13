

user_name = 'd135710'
password = 'Itsmyvsh838+'
api_key= 'PjVObAR5'
feed_token = None
token_map = None







# In[22]:


from smartapi.smartConnect import SmartConnect
import pandas as pd
import requests
import datetime
from threading import Timer
import time
from twilio.rest import Client
from datetime import datetime as date
import math


# In[31]:


client = Client("AC441d9d4dd5eda86b5814b88462526242","c4d8d14dfb9b20105734e2e9094b5f6e")

obj=SmartConnect(api_key=api_key)
data = obj.generateSession(user_name,password)
print(data)
refreshToken= data['data']['refreshToken']



# In[4]:
############################

feedToken=obj.getfeedToken()
feed_token=feedToken

print(feed_token)


# In[5]:


userProfile= obj.getProfile(refreshToken)
print(userProfile)


# In[6]:


url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
d = requests.get(url).json()
global token_df
token_df = pd.DataFrame.from_dict(d)
# token_df.to_csv('file1.csv')
token_df['expiry'] = pd.to_datetime(token_df['expiry'])
token_df = token_df.astype({'strike': float})
token_map = token_df


# In[7]:


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


# In[11]:


def absvalue(p):
    val = p
    val2 = math.fmod(val, 100)
    x = val - val2
    print(x,val,val2)
    abs_val = "{:.0f}".format(x)
    abs_val=int(abs_val)
    if val2>=50:
        abs_val=abs_val+100
    return abs_val


# In[12]:


def msg(m):
        message=client.messages.create(body=m,from_="whatsapp:+14155238886",to="whatsapp:+917386982737")


# In[16]:


peinfo1 = getTokenInfo('NFO','OPTIDX','NIFTY',18550,'PE').iloc[0]
pp=getpremium(peinfo1['symbol'],peinfo1['token'],'NFO')
pp


# In[98]:


while True:
            
    now = date.now()
    if now.hour!=4 and now.minute>=2:

        sp=getpremium('BANKNIFTY','26009','NSE')
        asp=absvalue(sp)
        print("strike",asp)
        msg("Strike"+str(asp))
        
        
        
        ceinfo = getTokenInfo('NFO','OPTIDX','BANKNIFTY',asp,'CE').iloc[0]
        peinfo = getTokenInfo('NFO','OPTIDX','BANKNIFTY',asp,'PE').iloc[0]
        cp=getpremium(ceinfo['symbol'],ceinfo['token'],'NFO')
        pp=getpremium(peinfo['symbol'],peinfo['token'],'NFO')
        
        
        print(ceinfo,peinfo,cp,pp)
        symbol  = ceinfo['symbol']
        token = ceinfo['token']
        lot = int(ceinfo['lotsize'])

        symbol1  = peinfo['symbol']
        token1 = peinfo['token']
        
        ce_order=place_order(token,symbol,lot,'NFO','SELL','MARKET',0)
        pe_order=place_order(peinfo['token'],peinfo['symbol'],lot,'NFO','SELL','MARKET',0)
        
        print(ce_order,pe_order)
        print(symbol,symbol1,"Strikes")

        msg(symbol)
        msg(symbol1)

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
            if now.hour==10 or getpremium(ceinfo['symbol'],ceinfo['token'],'NFO')<=cp_tp or getpremium(peinfo['symbol'],peinfo['token'],'NFO')<=pp_tp:
                place_order(ceinfo['token'],ceinfo['symbol'],lot,'NFO','BUY','MARKET',0)
                place_order(peinfo['token'],peinfo['symbol'],lot,'NFO','BUY','MARKET',0)
                profit_cp=(cp-getpremium(ceinfo['symbol'],ceinfo['token'],'NFO'))*25
                profit_pp=(pp-getpremium(peinfo['symbol'],peinfo['token'],'NFO'))*25
                msg(str(profit_cp))
                msg(str(profit_pp))


                c=2
                p=2
                
                print('Total P&L :',profit_cp+profit_pp)



                
                
            else :
                print('Call Premium :',cp_tp,getpremium(ceinfo['symbol'],ceinfo['token'],'NFO'),cp_sl)

                print('Put Premium :',pp_tp,getpremium(peinfo['symbol'],peinfo['token'],'NFO'),pp_sl)
        break
 
            
        
        
    else:
        print("Wait",now)
        

    
    
if c==0:
    
    print("Call Option Exited")
    msg("Call Option Exited")

    
    while True:
        tsl_pp=new_pp*1.2
        ttp_pp=new_pp*0.9
        now = date.now()

        if getpremium(peinfo['symbol'],peinfo['token'],'NFO')<=ttp_pp :
            new_pp=getpremium(peinfo['symbol'],peinfo['token'],'NFO')
            print("PUT New TP,SL :",new_pp*0.9,new_pp,new_pp*1.2)
            msg("PUT New TP : "+str(new_pp*0.9)+"Trigger"+str(new_pp)+"SL : "+str(new_pp*1.2))
        if getpremium(peinfo['symbol'],peinfo['token'],'NFO')>=tsl_pp or new_pp<=0.5*pp or now.hour==10:
            pp_amount=(pp-getpremium(peinfo['symbol'],peinfo['token'],'NFO'))*25
            place_order(peinfo['token'],peinfo['symbol'],lot,'NFO','BUY','MARKET',0)
            print('Total P&L :',loss_cp+pp_amount)
            msg("Total P&L :"+str(loss_cp+pp_amount))

            break
            
if p==0:
    
    print("Put Option Exited")
    msg("Put Option Exited")

    
    
    while True:
        tsl_cp=new_cp*1.2
        ttp_cp=new_cp*0.9
        now = date.now()

        
        if getpremium(ceinfo['symbol'],ceinfo['token'],'NFO')<=ttp_cp :
            new_cp=getpremium(ceinfo['symbol'],ceinfo['token'],'NFO')
            print("CALL New TP,SL :",new_cp*0.9,new_cp,new_cp*1.2)
            msg("CALL New TP : "+str(new_cp*0.9)+"Trigger"+str(new_cp)+"SL : "+str(new_cp*1.2))


        if getpremium(ceinfo['symbol'],ceinfo['token'],'NFO')>=tsl_cp or new_cp<=0.5*cp or now.hour==10 :
            cp_amount=(cp-getpremium(ceinfo['symbol'],ceinfo['token'],'NFO'))*25
            place_order(ceinfo['token'],ceinfo['symbol'],lot,'NFO','BUY','MARKET',0)
            print('Total P&L :',loss_pp+cp_amount)
            msg("Total P&L :"+str(loss_pp+cp_amount))
            
            break
        
        

            
            
        
        
        
        
        
        
        


# In[ ]:





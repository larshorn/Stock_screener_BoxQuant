import streamlit as st
st.set_page_config(layout="wide")
import yfinance as yf
import datetime 
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
import pandas as pd
import requests
yf.pdr_override()

st.write("""
# BoxQuant.no - Datadriven decitions\n
Technical Analysis Web Application \n
 **Shown below are the Moving Average Crossovers, Bollinger Bands, MACD's, Commodity Channel Indexes, Relative Strength Indexes and Extended Market Calculators of any stock!
**""")

st.sidebar.header('User Input Parameters')
st.sidebar.text('Norwegian stocs - add .OL \nSwedish stocks  - add .SE \nETC')
# Appends some text to the app.

#start = st.sidebar.date_input("Select start date",datetime.date(2007, 3, 6))

#Norway = st.sidebar.selectbox(
#    'Norwegian stocks',
#    ('Yes', 'No', ))

today = datetime.date.today()
def user_input_features():
    ticker = st.sidebar.text_input("Ticker", 'TEL.OL')
    start_date = st.sidebar.text_input("Start Date", '2019-01-01')
    end_date = st.sidebar.text_input("End Date", f'{today}')
    return ticker, start_date, end_date

symbol, start, end = user_input_features()

def get_symbol(symbol):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
    result = requests.get(url).json()
    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name']


company_name = get_symbol(symbol.upper())

start = pd.to_datetime(start)
end = pd.to_datetime(end)



Fast_sma=st.sidebar.slider(
    'Select variable simple moving average timespan',
    10, 250, step=(10))


# Read data 
data = yf.download(symbol,start,end)


# Adjusted Close Price
st.header(f"""Adjusted Close Price\n {company_name}""")
st.line_chart(data['Adj Close'])


# ## SMA and EMA
#Simple Moving Average
data['SMA_var'] = data['Adj Close'].rolling(Fast_sma).mean()
data['SMA_20']  = data['Adj Close'].rolling(20).mean()
data['SMA_50']  = data['Adj Close'].rolling(50).mean()
data['SMA_200'] = data['Adj Close'].rolling(200).mean()

# Add a selectbox to the sidebar:



# Exponential Moving Average
data['EMA'] = data['Adj Close'].ewm(span=20,adjust=False).mean()

## Plot
st.header(f"""Simple Moving Average vs. Exponential Moving Average\n {company_name}""")   
st.line_chart(data[['Adj Close','SMA_20','SMA_50','SMA_200','SMA_var','EMA']])

st.header(f"""Volume traded\n {company_name}""")   
st.bar_chart(data['Volume'])

# Bollinger Bands
data['middle_band'] = data['Adj Close'].rolling(20).mean()
data['upper_band'] = data['middle_band'] + data['Adj Close'].rolling(20).std(2)
data['lower_band'] =  data['middle_band'] - data['Adj Close'].rolling(20).std(2)



# Plot
st.header(f"""Bollinger Bands\n {company_name}, SMA = 20, STD =2""")
st.line_chart(data[['Adj Close','upper_band','middle_band','lower_band', 'SMA_200']])

# ## MACD (Moving Average Convergence Divergence)
# MACD

data['exp1'] = data['Adj Close'].ewm(span=12, adjust=False).mean()
data['exp2'] = data['Adj Close'].ewm(span=26, adjust=False).mean()

data['Macd'] = data['exp1']- data['exp2'] 
data['Madc_signal'] = data['Macd'].ewm(span=9, adjust=False).mean()


st.header(f"""Moving Average Convergence Divergence\n {company_name}""")
st.line_chart(data[['Macd','Madc_signal']])



## CCI (Commodity Channel Index)
# CCI
#cci = ta.trend.cci(data['High'], data['Low'], data['Close'], n=31, c=0.015)

# Plot
#st.header(f"""Commodity Channel Index\n {company_name}""")
#st.line_chart(cci)

# ## RSI (Relative Strength Index)
# RSI
##data['RSI'] = talib.RSI(data['Adj Close'], timeperiod=14)

# Plot
st.header(f"""Relative Strength Index\n {company_name}""")
#st.line_chart(data['RSI'])

# ## OBV (On Balance Volume)
# OBV
#data['OBV'] = talib.OBV(data['Adj Close'], data['Volume'])/10**6

# Plot
st.header(f"""
          On Balance Volume\n {company_name}
          """)
#st.line_chart(data['OBV'])

# Extended Market
fig, ax1 = plt.subplots() 

#Asks for stock ticker
sma = 50
limit = 10

data = yf.download(symbol,start, today)

#calculates sma and creates a column in the dataframe
data['SMA'+str(sma)] = data.iloc[:,4].rolling(window=sma).mean() 
data['PC'] = ((data["Adj Close"]/data['SMA'+str(sma)])-1)*100

mean = round(data["PC"].mean(), 2)
stdev = round(data["PC"].std(), 2)
current= round(data["PC"][-1], 2)
yday= round(data["PC"][-2], 2)

stats = [['Mean', mean], ['Standard Deviation', stdev], ['Current', current], ['Yesterday', yday]]

frame = pd.DataFrame(stats,
                   columns = ['Statistic', 'Value'])

st.header(f"""
          Extended Market Calculator\n {company_name}
          """)
st.dataframe(frame.style.hide_index())

# fixed bin size
bins = np.arange(-100, 100, 1) 
plt.rcParams['figure.figsize'] = 15, 10
plt.xlim([data["PC"].min()-5, data["PC"].max()+5])

plt.hist(data["PC"], bins=bins, alpha=0.5)
plt.title(symbol+"-- % From "+str(sma)+" SMA Histogram since "+str(start.year))
plt.xlabel('Percent from '+str(sma)+' SMA (bin size = 1)')
plt.ylabel('Count')

plt.axvline( x=mean, ymin=0, ymax=1, color='k', linestyle='--')
plt.axvline( x=stdev+mean, ymin=0, ymax=1, color='gray', alpha=1, linestyle='--')
plt.axvline( x=2*stdev+mean, ymin=0, ymax=1, color='gray',alpha=.75, linestyle='--')
plt.axvline( x=3*stdev+mean, ymin=0, ymax=1, color='gray', alpha=.5, linestyle='--')
plt.axvline( x=-stdev+mean, ymin=0, ymax=1, color='gray', alpha=1, linestyle='--')
plt.axvline( x=-2*stdev+mean, ymin=0, ymax=1, color='gray',alpha=.75, linestyle='--')
plt.axvline( x=-3*stdev+mean, ymin=0, ymax=1, color='gray', alpha=.5, linestyle='--')

plt.axvline( x=current, ymin=0, ymax=1, color='r', label = 'today')
plt.axvline( x=yday, ymin=0, ymax=1, color='blue', label = 'yesterday')

#add more x axis labels
ax1.xaxis.set_major_locator(mticker.MaxNLocator(14)) 

st.pyplot(fig)

#Create Plots
fig2, ax2 = plt.subplots() 

data=data[-150:]

data['PC'].plot(label='close',color='k')
plt.title(symbol+"-- % From "+str(sma)+" SMA Over last 100 days")
plt.xlabel('Date') 
plt.ylabel('Percent from '+str(sma)+' EMA')

#add more x axis labels
ax2.xaxis.set_major_locator(mticker.MaxNLocator(8)) 
plt.axhline( y=limit, xmin=0, xmax=1, color='r')
plt.rcParams['figure.figsize'] = 15, 10
st.pyplot(fig2)

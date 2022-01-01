## Importing the libraries
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import json
import requests
import base64
from PIL import Image
from bs4 import BeautifulSoup
from cryptocmd import CmcScraper
from autots import AutoTS
from plotly import graph_objs as go
import plotly.express as px


## Page layout
st.set_page_config(layout="wide")

## Title
st.markdown('# Crypto Vault')
st.markdown("""
    Interactive Cryptocurrency prices and charts for In-Depth Analysis, listed by market capitalization
    """)

## Title Wallpaper
image = Image.open('logo/title_logo.png')
st.image(image, width = 1000, use_column_width = 'auto')

## About Cryptocurrency
expander_bar = st.expander("What is Cryptocurrency?")
expander_bar.markdown("""
    A cryptocurrency is a digital or virtual currency that is secured by cryptography, which makes it nearly impossible to counterfeit or double-spend. Many cryptocurrencies are decentralized networks based on blockchain technology—a distributed ledger enforced by a disparate network of computers. A defining feature of cryptocurrencies is that they are generally not issued by any central authority, rendering them theoretically immune to government interference or manipulation.
    \n  
    Cryptocurrencies are systems that allow for secure payments online which are denominated in terms of virtual "tokens," which are represented by ledger entries internal to the system. "Crypto" refers to the various encryption algorithms and cryptographic techniques that safeguard these entries, such as elliptical curve encryption, public-private key pairs, and hashing functions.
    \n
    Cryptocurrencies hold the promise of making it easier to transfer funds directly between two parties, without the need for a trusted third party like a bank or credit card company. These transfers are instead secured by the use of public keys and private keys and different forms of incentive systems, like Proof of Work or Proof of Stake.
    \n
    In modern cryptocurrency systems, a user's "wallet," or account address, has a public key, while the private key is known only to the owner and is used to sign transactions. Fund transfers are completed with minimal processing fees, allowing users to avoid the steep fees charged by banks and financial institutions for wire transfers.
    """)

## Selectbox
coin_bar = st.selectbox("Select a COIN"
    ,
    ('Select' ,'BTC  (Bitcoin)', 'ETH  (Ethereum)', 'BNB  (Binance Coin)', 'ADA  (Cardano)', 'USDT (Tether)', 'XRP  (Ripple)', 'SOL  (Solana)', 'DOT  (Polkadot)', 'DOGE (Dogecoin)', 'UNI  (Uniswap)')
)

## Function for candlestick
def candlestick():

    fig = go.Figure(data=[go.Candlestick(x=df2['Date'],
                open=df2['Open'],
                high=df2['High'],
                low=df2['Low'],
                close=df2['Close'])])
    
    fig.update_layout(width=1100, height = 700, margin=dict(l=150),
     title = "Time Series Chart", xaxis_title = "Time Period", yaxis_title = "Price in USD",
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="1M",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6M",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="YTD",
                     step="year",
                     stepmode="todate"),
                dict(count=1,
                     label="1Y",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
     )

    st.plotly_chart(fig)

# Function for forecasting
def prediction():

    model = AutoTS(forecast_length=day_count, frequency='infer', ensemble='simple', drop_data_older_than_periods=100)
    model = model.fit(df2, date_col='Date', value_col='Close', id_col=None)
    predict = model.predict()
    final_forecast = predict.forecast
    col12.write(final_forecast)

## Sidebar
col1 = st.sidebar
col1.header('Navigation')

## Web scraping of Cryptocurrency Data from coinmarketcap.com
@st.cache
def load_data():
    cmc = requests.get('https://coinmarketcap.com/all/views/all/')
    soup = BeautifulSoup(cmc.content, 'html.parser')

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    for i in listings:
      coins[str(i['id'])] = i['slug']

    coin_name = []
    Symbol = []
    marketCap = []
    percentChange1h = []
    percentChange24h = []
    percentChange7d = []
    price = []
    volume24h = []

    for i in listings:
      coin_name.append(i['slug'])
      Symbol.append(i['symbol'])
      price.append(i['quote']['USD']['price'])
      percentChange1h.append(i['quote']['USD']['percentChange1h'])
      percentChange24h.append(i['quote']['USD']['percentChange24h'])
      percentChange7d.append(i['quote']['USD']['percentChange7d'])
      marketCap.append(i['quote']['USD']['marketCap'])
      volume24h.append(i['quote']['USD']['volume24h'])

    df = pd.DataFrame(columns=['Name', 'Price', 'Symbol', 'Market Cap ($)', '1h Change (%)', '24h Change (%)', '7d Change (%)', 'Volume (24h) ($)'])
    df['Name'] = coin_name
    df['Symbol'] = Symbol
    df['Price'] = price
    df['1h Change (%)'] = percentChange1h
    df['24h Change (%)'] = percentChange24h
    df['7d Change (%)'] = percentChange7d
    df['Market Cap ($)'] = marketCap
    df['Volume (24h) ($)'] = volume24h
    return df


df = load_data()

## Sidebar - Number of coins to display
num_coin = col1.slider('Select a number to display TOP N coins', 1, 40, 40)

## Sidebar - Cryptocurrency selections
sorted_coin =  df['Symbol'].head(40)
selected_coin = col1.multiselect('Select Multiple Cryptocurrency', sorted_coin, sorted_coin)
df_selected_coin = df[ (df['Symbol'].isin(selected_coin)) ] 
df_coins = df_selected_coin[:num_coin]


## If-Else for SelectBox

if coin_bar == 'BTC  (Bitcoin)':

    col2, col3, col4 = st.columns((3))
    btc_logo = Image.open('logo/btc_logo.png')
    col2.image(btc_logo, width = 100)

    df1 = df[df['Symbol'].str.contains('BTC')]
    col3.metric("Current Price of BTC ($)", df1.iloc[0]['Price'], df1.iloc[0]['24h Change (%)'] )

    col4.markdown("""
        * [Official Website](https://bitcoin.org/)
        * [White Paper](https://bitcoin.org/bitcoin.pdf)
        * [Source Code](https://github.com/bitcoin/)
        """)

    scraper = CmcScraper("BTC")
    df2 = scraper.get_dataframe()
    candlestick()

    col11,col12 = st.columns((2))
    col11.markdown(""" ### What is Bitcoin?  """)
    col11.markdown("""
        Bitcoin is a decentralized cryptocurrency originally described in a 2008 whitepaper by a person, or group of people, using the alias Satoshi Nakamoto. It was launched soon after, in January 2009. Bitcoin is a peer-to-peer online currency, meaning that all transactions happen directly between equal, independent network participants, without the need for any intermediary to permit or facilitate them. Bitcoin was created, according to Nakamoto’s own words, to allow “online payments to be sent directly from one party to another without going through a financial institution.” Some concepts for a similar type of a decentralized electronic currency precede BTC, but Bitcoin holds the distinction of being the first-ever cryptocurrency to come into actual use.
        """)

    col12.markdown(""" ### Forecasting  """)
    day_count = col12.slider('Select Number of days to predict', 1, 50, 1)

    if col12.button("Click for predicting price"):
        prediction()

elif coin_bar == 'ETH  (Ethereum)':

    col2, col3, col4 = st.columns((3))
    eth_logo = Image.open('logo/eth_logo.png')
    col2.image(eth_logo, width = 100)

    df1 = df[df['Symbol'].str.contains('ETH')]
    col3.metric("Current Price of ETH ($)", df1.iloc[0]['Price'], df1.iloc[0]['24h Change (%)'] )

    col4.markdown("""
        * [Official Website](https://ethereum.org/en/)
        * [White Paper](https://ethereum.org/en/whitepaper/)
        * [Source Code](https://github.com/ethereum)
        """)

    scraper = CmcScraper("ETH")
    df2 = scraper.get_dataframe()
    candlestick()

    col11,col12 = st.columns((2))
    col11.markdown(""" ### What is Ethereum?  """)
    col11.markdown("""
        Ethereum is a decentralized open-source blockchain system that features its own cryptocurrency, Ether. ETH works as a platform for numerous other cryptocurrencies, as well as for the execution of decentralized smart contracts. Ethereum was first described in a 2013 whitepaper by Vitalik Buterin. Buterin, along with other co-founders, secured funding for the project in an online public crowd sale in the summer of 2014. The project team managed to raise $18.3 million in Bitcoin, and Ethereum’s price in the Initial Coin Offering (ICO) was $0.311, with over 60 million Ether sold. Taking Ethereum’s price now, this puts the return on investment (ROI) at an annualized rate of over 270%, essentially almost quadrupling your investment every year since the summer of 2014. The Ethereum Foundation officially launched the blockchain on July 30, 2015, under the prototype codenamed “Frontier.” Since then, there has been several network updates — “Constantinople” on Feb. 28, 2019, “Istanbul” on Dec. 8, 2019, “Muir Glacier” on Jan. 2, 2020, “Berlin” on April 14, 2021, and most recently on Aug. 5, 2021, the “London” hard fork. Ethereum’s own purported goal is to become a global platform for decentralized applications, allowing users from all over the world to write and run software that is resistant to censorship, downtime and fraud.
        """)

    col12.markdown(""" ### Forecasting  """)
    day_count = col12.slider('Select Number of days to predict', 1, 50, 1)

    if col12.button("Click for predicting price"):
        prediction()


elif coin_bar == 'BNB  (Binance Coin)':

    col2, col3, col4 = st.columns((3))
    bnb_logo = Image.open('logo/bnb_logo.png')
    col2.image(bnb_logo, width = 100)

    df1 = df[df['Symbol'].str.contains('BNB')]
    col3.metric("Current Price of BNB ($)", df1.iloc[0]['Price'], df1.iloc[0]['24h Change (%)'] )

    col4.markdown("""
        * [Official Website](https://www.binance.com/en)
        * [White Paper](https://github.com/binance-chain/whitepaper/blob/master/WHITEPAPER.md)
        * [Source Code](https://github.com/binance-chain)
        """)

    scraper = CmcScraper("BNB")
    df2 = scraper.get_dataframe()
    candlestick()

    col11,col12 = st.columns((2))
    col11.markdown(""" ### What is Binance Coin?  """)
    col11.markdown("""
        Launched in July 2017, Binance is the biggest cryptocurrency exchange globally based on daily trading volume. Binance aims to bring cryptocurrency exchanges to the forefront of financial activity globally. The idea behind Binance’s name is to show this new paradigm in global finance — Binary Finance, or Binance. Aside from being the largest cryptocurrency exchange globally, Binance has launched a whole ecosystem of functionalities for its users. The Binance network includes the Binance Chain, Binance Smart Chain, Binance Academy, Trust Wallet and Research projects, which all employ the powers of blockchain technology to bring new-age finance to the world. Binance Coin is an integral part of the successful functioning of many of the Binance sub-projects.
        """)

    col12.markdown(""" ### Forecasting  """)
    day_count = col12.slider('Select Number of days to predict', 1, 50, 1)

    if col12.button("Click for predicting price"):
        prediction()

elif coin_bar == 'ADA  (Cardano)':

    col2, col3, col4 = st.columns((3))
    ada_logo = Image.open('logo/ada_logo.png')
    col2.image(ada_logo, width = 100)

    df1 = df[df['Symbol'].str.contains('ADA')]
    col3.metric("Current Price of ADA ($)", df1.iloc[0]['Price'], df1.iloc[0]['24h Change (%)'] )

    col4.markdown("""
        * [Official Website](https://www.cardano.org/)
        * [White Paper](https://docs.cardano.org/en/latest/)
        * [Source Code](https://cardanoupdates.com/)
        """)

    scraper = CmcScraper("ADA")
    df2 = scraper.get_dataframe()
    candlestick()

    col11,col12 = st.columns((2))
    col11.markdown(""" ### What is Cardano?  """)
    col11.markdown("""
        Cardano is a proof-of-stake blockchain platform that says its goal is to allow “changemakers, innovators and visionaries” to bring about positive global change.Cardano was founded back in 2017, and named after the 16th century Italian polymath Gerolamo Cardano.The open-source project also aims to “redistribute power from unaccountable structures to the margins to individuals” — helping to create a society that is more secure, transparent and fair.
        """)

    col12.markdown(""" ### Forecasting  """)
    day_count = col12.slider('Select Number of days to predict', 1, 50, 1)

    if col12.button("Click for predicting price"):
        prediction()

elif coin_bar == 'USDT (Tether)':

    col2, col3, col4 = st.columns((3))
    usdt_logo = Image.open('logo/usdt_logo.png')
    col2.image(usdt_logo, width = 100)

    df1 = df[df['Symbol'].str.contains('USDT')]
    col3.metric("Current Price of USDT ($)", df1.iloc[0]['Price'], df1.iloc[0]['24h Change (%)'] )

    col4.markdown("""
        * [Official Website](https://tether.to/)
        * [White Paper](https://tether.to/wp-content/uploads/2016/06/TetherWhitePaper.pdf)
        * [Source Code](https://gist.github.com/plutoegg/a8794a24dfa84d0b0104141612b52977)
        """)

    scraper = CmcScraper("ADA")
    df2 = scraper.get_dataframe()
    candlestick()

    col11,col12 = st.columns((2))
    col11.markdown(""" ### What is USDT (Tether)?  """)
    col11.markdown("""
        USDT is a stablecoin (stable-value cryptocurrency) which was launched in 2014 by Brock Pierce, Reeve Collins and Craig Sellars, that mirrors the price of the U.S. dollar, issued by a Hong Kong-based company Tether. The token’s peg to the USD is achieved via maintaining a sum of commercial paper, fiduciary deposits, cash, reserve repo notes, and treasury bills in reserves that is equal in USD value to the number of USDT in circulation.It's a second-layer cryptocurrency token built on top of Bitcoin’s blockchain through the use of the Omni platform, it was later renamed to USTether, and then, finally, to USDT.
        """)

    col12.markdown(""" ### Forecasting  """)
    day_count = col12.slider('Select Number of days to predict', 1, 50, 1)

    if col12.button("Click for predicting price"):
        prediction()

elif coin_bar == 'XRP  (Ripple)':

    col2, col3, col4 = st.columns((3))
    xrp_logo = Image.open('logo/xrp_logo.png')
    col2.image(xrp_logo, width = 100)

    df1 = df[df['Symbol'].str.contains('XRP')]
    col3.metric("Current Price of XRP ($)", df1.iloc[0]['Price'], df1.iloc[0]['24h Change (%)'] )

    col4.markdown("""
        * [Official Website](https://xrpl.org/)
        * [White Paper](https://ripple.com/files/ripple_consensus_whitepaper.pdf)
        * [Source Code](https://github.com/ripple)
        """)

    scraper = CmcScraper("XRP")
    df2 = scraper.get_dataframe()
    candlestick()

    col11,col12 = st.columns((2))
    col11.markdown(""" ### What is Ripple?  """)
    col11.markdown("""
        XRP is the currency that runs on a digital payment platform called RippleNet, which is on top of a distributed ledger database called XRP Ledger. While RippleNet is run by a company called Ripple, the XRP Ledger is open-source and is not based on blockchain, but rather the previously mentioned distributed ledger database.The RippleNet payment platform is a real-time gross settlement (RTGS) system that aims to enable instant monetary transactions globally.
        """)

    col12.markdown(""" ### Forecasting  """)
    day_count = col12.slider('Select Number of days to predict', 1, 50, 1)

    if col12.button("Click for predicting price"):
        prediction()
        
elif coin_bar == 'SOL  (Solana)':

    col2, col3, col4 = st.columns((3))
    sol_logo = Image.open('logo/sol_logo.png')
    col2.image(sol_logo, width = 100)

    df1 = df[df['Symbol'].str.contains('SOL')]
    col3.metric("Current Price of SOL ($)", df1.iloc[0]['Price'], df1.iloc[0]['24h Change (%)'] )

    col4.markdown("""
        * [Official Website](https://solana.com/)
        * [White Paper](https://solana.com/solana-whitepaper.pdf)
        * [Source Code](https://github.com/solana-labs)
        """)

    scraper = CmcScraper("SOL")
    df2 = scraper.get_dataframe()
    candlestick()

    col11,col12 = st.columns((2))
    col11.markdown(""" ### What is Solana?  """)
    col11.markdown("""
        Solana is a highly functional open source project that banks on blockchain technology’s permissionless nature to provide decentralized finance (DeFi) solutions. While the idea and initial work on the project began in 2017, Solana was officially launched in March 2020 by the Solana Foundation with headquarters in Geneva, Switzerland.The Solana protocol is designed to facilitate decentralized app (DApp) creation. It aims to improve scalability by introducing a proof-of-history (PoH) consensus combined with the underlying proof-of-stake (PoS) consensus of the blockchain.One of the essential innovations Solana brings to the table is the proof-of-history (PoH) consensus developed by Anatoly Yakovenko. This concept allows for greater scalability of the protocol, which in turn boosts usability.
        """)

    col12.markdown(""" ### Forecasting  """)
    day_count = col12.slider('Select Number of days to predict', 1, 50, 1)

    if col12.button("Click for predicting price"):
        prediction()
        

elif coin_bar == 'DOT  (Polkadot)':

    col2, col3, col4 = st.columns((3))
    dot_logo = Image.open('logo/dot_logo.png')
    col2.image(dot_logo, width = 100)

    df1 = df[df['Symbol'].str.contains('DOT')]
    col3.metric("Current Price of DOT ($)", df1.iloc[0]['Price'], df1.iloc[0]['24h Change (%)'] )

    col4.markdown("""
        * [Official Website](https://polkadot.network/)
        * [White Paper](https://polkadot.network/PolkaDotPaper.pdf)
        * [Source Code](https://github.com/w3f)
        """)

    scraper = CmcScraper("DOT")
    df2 = scraper.get_dataframe()
    candlestick()

    col11,col12 = st.columns((2))
    col11.markdown(""" ### What is Polkadot?  """)
    col11.markdown("""
        Polkadot is an open-source sharding multichain protocol that facilitates the cross-chain transfer of any data or asset types, not just tokens, thereby making a wide range of blockchains interoperable with each other.This interoperability seeks to establish a fully decentralized and private web, controlled by its users, and simplify the creation of new applications, institutions and services.The Polkadot protocol connects public and private chains, permissionless networks, oracles and future technologies, allowing these independent blockchains to trustlessly share information and transactions through the Polkadot relay chain (explained further down).
        """)

    col12.markdown(""" ### Forecasting  """)
    day_count = col12.slider('Select Number of days to predict', 1, 50, 1)

    if col12.button("Click for predicting price"):
        prediction()
     
     
elif coin_bar == 'DOGE (Dogecoin)':

    col2, col3, col4 = st.columns((3))
    doge_logo = Image.open('logo/doge_logo.png')
    col2.image(doge_logo, width = 100)

    df1 = df[df['Symbol'].str.contains('DOGE')]
    col3.metric("Current Price of DOGE ($)", df1.iloc[0]['Price'], df1.iloc[0]['24h Change (%)'] )

    col4.markdown("""
        * [Official Website](http://dogecoin.com/)
        * [White Paper](https://github.com/dogecoin/dogecoin/blob/master/README.md)
        * [Source Code](https://github.com/dogecoin/dogecoin)
        """)

    scraper = CmcScraper("DOGE")
    df2 = scraper.get_dataframe()
    candlestick()

    col11,col12 = st.columns((2))
    col11.markdown(""" ### What is Dogecoin?  """)
    col11.markdown("""
        Dogecoin (DOGE) is based on the popular "doge" Internet meme and features a Shiba Inu on its logo. The open-source digital currency was created by Billy Markus from Portland, Oregon and Jackson Palmer from Sydney, Australia, and was forked from Litecoin in December 2013. Dogecoin's creators envisaged it as a fun, light-hearted cryptocurrency that would have greater appeal beyond the core Bitcoin audience, since it was based on a dog meme. Tesla CEO Elon Musk posted several tweets on social media that Dogecoin is his favorite coin.
        """)

    col12.markdown(""" ### Forecasting  """)
    day_count = col12.slider('Select Number of days to predict', 1, 50, 1)

    if col12.button("Click for predicting price"):
        prediction()
        
elif coin_bar == 'UNI  (Uniswap)':

    col2, col3, col4 = st.columns((3))
    uni_logo = Image.open('logo/uni_logo.png')
    col2.image(uni_logo, width = 100)

    df1 = df[df['Symbol'].str.contains('UNI')]
    col3.metric("Current Price of UNI ($)", df1.iloc[0]['Price'], df1.iloc[0]['24h Change (%)'] )

    col4.markdown("""
        * [Official Website](https://uniswap.org/)
        * [White Paper](https://uniswap.org/whitepaper.pdf)
        * [Source Code](https://github.com/Uniswap)
        """)

    scraper = CmcScraper("UNI")
    df2 = scraper.get_dataframe()
    candlestick()

    col11,col12 = st.columns((2))
    col11.markdown(""" ### What is Uniswap?  """)
    col11.markdown("""
        Uniswap is a popular decentralized trading protocol, known for its role in facilitating automated trading of decentralized finance (DeFi) tokens.An example of an automated market maker (AMM), Uniswap launched in November 2018, but has gained considerable popularity this year thanks to the DeFi phenomenon and associated surge in token trading.Uniswap aims to keep token trading automated and completely open to anyone who holds tokens, while improving the efficiency of trading versus that on traditional exchanges.Uniswap creates more efficiency by solving liquidity issues with automated solutions, avoiding the problems which plagued the first decentralized exchanges.
        """)

    col12.markdown(""" ### Forecasting  """)
    day_count = col12.slider('Select Number of days to predict', 1, 50, 1)

    if col12.button("Click for predicting price"):
        prediction()





## Page Break
st.markdown("----------------")

## For coloring percentage
def color_percent(value):

  if value < 0:
    color = 'red'
  elif value > 0:
    color = 'green'
  else:
    color = 'black'

  return 'color: %s' % color


## Main Table
st.subheader('Cryptocurrency Market Info')
st.write('Table has ' + str(df_selected_coin.shape[0]) + ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')
df_coins = df_coins.style.applymap(color_percent, subset=['1h Change (%)','24h Change (%)', '7d Change (%)']).format({('1h Change (%)'): "{:,.2f}%", ('24h Change (%)'): "{:,.2f}%", ('7d Change (%)'): "{:,.2f}%" , ('Price'): "${:,.3f}" , ('Market Cap ($)'): "${:,.0f}" , ('Volume (24h) ($)'): "${:,.0f}"})
st.dataframe(df_coins, width = 2000, height = 2000)


## For Charts

col5, col6 = st.columns((1,1))

def plot_raw_data2():
    fig = px.pie(df.head(10), values='Market Cap ($)', names='Symbol')
    fig.update_layout(width=500, height = 500, title = "Top 10 Cryptocurrency by Market Cap")
    col5.plotly_chart(fig)
plot_raw_data2()

def plot_raw_data2():
    fig = px.bar(df.head(40), x='7d Change (%)', y='Symbol', orientation='h')
    fig.update_layout(width=500, height = 500, title = "Top 40 Cryptocurrency by 7d Change (%)")
    col6.plotly_chart(fig)
plot_raw_data2()


# For About us, Glossary and FAQ

col8, col9, col10 = col1.columns((1,1,1))

page1 = col8.button("About Us")
page2 = col9.button("Glossary")
page3 = col10.button("FAQ")

if page1:

    col1.markdown("""
    We are a CryptoCurrency organisation aiming to bring this digital revolution to each and every person in the world by means of our digital dashboard tool named "Crypto Vault".
    \n
    Crypto Vault is a one stop solution for beginners as well as experienced individuals who want to pursue their interests in this domain. We provide the quickest and the most relevant information to our users through our state of the art algorithms and architecture. The services we provide include coin data retrieval, predictive analsysis and forecasting for several coins that are deemed most relevant and popular in today's time and that too absolutely free!!!!!!!. This makes us one of the best resources for Cryptocurrencies around the world.
    \n
    Disclaimer - We are by no means providing you investment advice and it must be handled by user at their own discretion.
             """)

elif page2:

    col1.markdown("""## 1hr""")
    col1.markdown("""
    Stands for the data for the past 1hr.
        """)
    col1.markdown("""## 24hr""")
    col1.markdown("""
    Stands for the data for the past 24hr.
        """)
    col1.markdown("""## 7d""")
    col1.markdown("""
    Stands for the data for the past 7 days.
        """)
    col1.markdown("""## Algorithms""")
    col1.markdown("""
    A process or set of rules to be followed in problem-solving or calculation operations, usually by a computer.
        """)
    col1.markdown("""## Blockchain""")
    col1.markdown("""
    A distributed ledger system. A sequence of blocks, or units of digital information, stored consecutively in a public database. The basis for cryptocurrencies.
       """)
    col1.markdown("""## Candlestick Chart""")
    col1.markdown("""
    A candlestick chart is a graphing technique used to show changes in price over time. Each candle provides 4 points of information opening price, closing price, high, and low. Also known as “candles” for short.       """)
    col1.markdown("""## Decentralized Currency""")
    col1.markdown("""
    Decentralized currency refers to bank-free methods of transferring wealth or ownership of any other commodity without needing a third party.
        """)
    col1.markdown("""## MarketCap""")
    col1.markdown("""
    It is the total value of all the coins that have been mined.        
        """)
    col1.markdown("""## Trust""")
    col1.markdown("""
    A trust is a fiduciary relationship in which one party, known as a trustor, gives another party, the trustee, the right to hold title to property or assets for the benefit of a third party, the beneficiary. 
       """)
    col1.markdown("""## Volume""")
    col1.markdown("""
    It simply the total amount of coins traded in the last 24 hours. 
       """)
    col1.markdown("""## YTD""")
    col1.markdown("""
    Stands for year to date.
       """)

elif page3:

    expander_bar = col1.expander("What is Market Capitalization and how is it calculated?")
    expander_bar.markdown("""
    Market Capitalization is one way to rank the relative size of a cryptocurrency.
    \n
    It's calculated by multiplying the Price by the Circulating Supply.
    \n
    Market Cap = Price X Circulating Supply.""")
    expander_bar = col1.expander("What is the difference between a Coin and a Token on the site??")
    expander_bar.markdown("""
    A Coin is a cryptocurrency that can operate independently.
    \n
    A Token is a cryptocurrency that depends on another cryptocurrency as a platform to operate.    
    """)
    expander_bar = col1.expander("Is Bitcoin vulnerable to quantum computing?")
    expander_bar.markdown("""
    Yes, most systems relying on cryptography in general are, including traditional banking systems. However, quantum computers don't yet exist and probably won't for a while. In the event that quantum computing could be an imminent threat to Bitcoin, the protocol could be upgraded to use post-quantum algorithms. Given the importance that this update would have, it can be safely expected that it would be highly reviewed by developers and adopted by all Bitcoin users.
    """)
    expander_bar = col1.expander("Who created Bitcoin?")
    expander_bar.markdown("""
    Bitcoin’s existence began with an academic paper written in 2008 by a developer under the name of Satoshi Nakamoto.
    \n
    The paper described the foundation for what was intended to be a peer-to-peer electronic cash system that was secure, affordable, and efficient far beyond conventional banking standards. The system Satoshi described was developed into open-source software and the first bitcoin transaction (also known as the Genesis Block) was confirmed on January 3, 2009.
    """)
    expander_bar = col1.expander("How does blockchain work?")
    expander_bar.markdown("""
    Blockchain technology connects millions of computers (much like the internet) that can all store/host encrypted copies of these records. So instead of one record keeper, you have millions of record keepers called 'nodes'. One record keeper can tamper records, collude with third parties and commit fraud, but now there are a million nodes who are keeping a watch on each other. Much like the internet provides an infrastructure for communication, blockchain provides an infrastructure for record keeping.
    """)
    expander_bar = col1.expander("Why do people trust Bitcoin?")
    expander_bar.markdown("""
    Much of the trust in Bitcoin comes from the fact that it requires no trust at all. Bitcoin is fully open-source and decentralized. This means that anyone has access to the entire source code at any time. Any developer in the world can therefore verify exactly how Bitcoin works. All transactions and bitcoins issued into existence can be transparently consulted in real-time by anyone. All payments can be made without reliance on a third party and the whole system is protected by heavily peer-reviewed cryptographic algorithms like those used for online banking. No organization or individual can control Bitcoin, and the network remains secure even if not all of its users can be trusted.
    """)
    expander_bar = col1.expander("In what time zone is the site based?")
    expander_bar.markdown("""
    Data is collected, recorded, and reported in UTC time unless otherwise specified.
    """)

else:

    print("")

## END














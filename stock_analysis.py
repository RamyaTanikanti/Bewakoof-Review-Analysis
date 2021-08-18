# Import libraries
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# NLTK VADER for sentiment analysis
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# Extract tables
from html_table_parser.parser import HTMLTableParser
# UI
import streamlit as st
# To play with dates
import datetime
from datetime import date as dt
from datetime import datetime
from datetime import timedelta
import timeago
import plotly.express as px

# App title
st.title('Know Your Stocks Better')
st.write('Understand how people feel about stocks.')

finwiz_url = 'https://finviz.com/quote.ashx?t='
finwiz_search_url = 'https://finviz.com/search.ashx?p='

search_term = st.text_input('Enter company name')
if search_term:
    search_url=finwiz_search_url+search_term.upper()
    st.write(search_url)
    req = Request(url=search_url,headers={'user-agent': 'my-app/0.0.1'})
    f = urlopen(req)
    xhtml = f.read().decode('utf-8')
    p = HTMLTableParser()
    p.feed(xhtml)
    parsed_and_scored_news=pd.DataFrame(p.tables[5])
    parsed_and_scored_news=parsed_and_scored_news.rename(columns=parsed_and_scored_news.iloc[0])[1:][['Ticker','Description']]
    st.write("Search Results for {}:\n".format(search_term))
    st.write(parsed_and_scored_news)
    tickers=[]
    ticker=st.text_input("Enter company ticker: ").upper()
    if ticker:
        tickers.append(ticker)
    
        news_tables = {}
        for ticker in tickers:
            url = finwiz_url + ticker
            req = Request(url=url,headers={'user-agent': 'my-app/0.0.1'}) 
            response = urlopen(req)    
            # Read the contents of the file into 'html'
            html = BeautifulSoup(response)
            # Find 'news-table' in the Soup and load it into 'news_table'
            news_table = html.find(id='news-table')
            # Add the table to our dictionary
            news_tables[ticker] = news_table
        
        parsed_news = []
        # Iterate through the news
        for file_name, news_table in news_tables.items():
            # Iterate through all tr tags in 'news_table'
            for x in news_table.findAll('tr'):
                # read the text from each tr tag into text
                # get text from a only
                text = x.a.get_text() 
                # splite text in the td tag into a list 
                date_scrape = x.td.text.split()
                # if the length of 'date_scrape' is 1, load 'time' as the only element

                if len(date_scrape) == 1:
                    time = date_scrape[0]
            
                # else load 'date' as the 1st element and 'time' as the second    
                else:
                    date = date_scrape[0]
                    time = date_scrape[1]
                # Extract the ticker from the file name, get the string up to the 1st '_'  
                ticker = file_name.split('_')[0]
        
                # Append ticker, date, time and headline as a list to the 'parsed_news' list
                parsed_news.append([ticker, date, time, text])

        # Set column names
        columns = ['ticker', 'date', 'time', 'headline']

        # Convert the parsed_news list into a DataFrame called 'parsed_and_scored_news'
        parsed_and_scored_news = pd.DataFrame(parsed_news, columns=columns)
    
        # Transforming Dates
        parsed_and_scored_news['Time'] = parsed_and_scored_news['time'].str[:5]
        parsed_and_scored_news['Unit'] = parsed_and_scored_news['time'].str[5:]
        parsed_and_scored_news['Time'] = parsed_and_scored_news['Time']+' '+parsed_and_scored_news['Unit']
        parsed_and_scored_news.drop('Unit',axis=1,inplace=True)
        parsed_and_scored_news['Time'] = parsed_and_scored_news['Time'].str.strip()
        Time = []
        for time in parsed_and_scored_news['Time']:
            in_time = datetime.strptime(time, "%I:%M %p")
            out_time = datetime.strftime(in_time, "%H:%M")
            Time.append(out_time)
        parsed_and_scored_news['time'] = Time
        parsed_and_scored_news.drop('Time',axis=1,inplace=True)
        parsed_and_scored_news['date'] = parsed_and_scored_news['date'].astype('str')
        parsed_and_scored_news['datetime'] = parsed_and_scored_news['date']+' '+parsed_and_scored_news['time']

        parsed_and_scored_news['datetime'] = pd.to_datetime(parsed_and_scored_news['datetime'])
        parsed_and_scored_news['date'] = pd.to_datetime(parsed_and_scored_news['date'])

        relativetime = []
        now = datetime.now()
        for time in parsed_and_scored_news['datetime']:
            t = timeago.format(time, now)
            relativetime.append(t)
        parsed_and_scored_news['timeago'] = relativetime
    
        # Drop duplicates based on ticker and headline
        parsed_and_scored_news_clean = parsed_and_scored_news.drop_duplicates(subset=['headline', 'ticker'])
    
        # Instantiate the sentiment intensity analyzer
        vader = SentimentIntensityAnalyzer()

        # Iterate through the headlines and get the polarity scores using vader
        scores = parsed_and_scored_news_clean['headline'].apply(vader.polarity_scores).tolist()

        # Convert the 'scores' list of dicts into a DataFrame
        scores_df = pd.DataFrame(scores)

        # Join the DataFrames of the news and the list of dicts
        parsed_and_scored_news_clean = parsed_and_scored_news_clean.join(scores_df, rsuffix='_right')

        # Overall Sentiment
        parsed_and_scored_news_clean['Sentiment'] = np.where(parsed_and_scored_news_clean['compound']>=0.05,'Positive','Neutral')
        parsed_and_scored_news_clean['Sentiment'] = np.where(parsed_and_scored_news_clean['compound']<=0.05,'Negative',parsed_and_scored_news_clean['Sentiment'])

        n = st.text_input("Enter a number i.e., enter 2 if you want to see the yesterday's sentiment:")
        if n:
            n = int(n)
            todayDate = pd.to_datetime(dt.today())
            filterdate = str((pd.to_datetime(todayDate - timedelta(days = n))).date())
            df = parsed_and_scored_news_clean[parsed_and_scored_news_clean['date']==filterdate]
            df = df.groupby(['datetime','Sentiment'])['headline'].count().reset_index()
            df.rename(columns={'headline':'Count'},inplace=True)
            fig = px.line(df, x='datetime', y='Count', color='Sentiment', markers=True)
            fig.show()
            st.plotly_chart(fig)
        else:
            st.warning('Please enter a number!')

    else:
        st.warning('Please enter ticker!')

else:
    st.warning('Please enter company name!')
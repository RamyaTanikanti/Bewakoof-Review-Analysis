# Import libraries
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
# Extract tables
from html_table_parser.parser import HTMLTableParser
import time, datetime
import pandas as pd
import numpy as np
# NLTK VADER for sentiment analysis
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import streamlit as st


def scraping_and_cleaning(tickers):
    finwiz_url = 'https://finviz.com/quote.ashx?t='
    
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
    parsed_and_scored_news['date'] = pd.to_datetime(parsed_and_scored_news.date).dt.date

    # Drop duplicates based on ticker and headline
    parsed_and_scored_news_clean = parsed_and_scored_news.drop_duplicates(subset=['headline', 'ticker'])

    # Transforming Dates
    parsed_and_scored_news['date'] = pd.to_datetime(parsed_and_scored_news.date).dt.date

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
    parsed_and_scored_news_clean['Sentiment'] = np.where(parsed_and_scored_news_clean['compound']>=0.5,'Positive','Neutral')
    parsed_and_scored_news_clean['Sentiment'] = np.where(parsed_and_scored_news_clean['compound']<= -0.5,'Negative',parsed_and_scored_news_clean['Sentiment'])

    return parsed_and_scored_news_clean
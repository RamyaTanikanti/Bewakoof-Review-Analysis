import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import parsing_and_scoring

# App title
st.title('Know Your Stocks Better')
st.write('Understand how people feel about stocks.')

df = st.cache(pd.read_csv)("C:/Users/Ramya/Downloads/GitHub Projects/Stock Prediction From Financial News/Scraping-Screener-Table-Contents/screener_table_contents.csv")

tickers=[]
st.header('Enter Company Name(s)')
options = st.multiselect('',df['Company'].unique())

if options and len(options) <= 3:
    st.write('You selected,')
    for company in options:
        tickers.append(df[df['Company']==company]['Ticker'].values[0])
        st.write(df[df['Company']==company]['Ticker'].values[0],':',company)
    
    # Date Picker
    df_scored = parsing_and_scoring.scraping_and_cleaning(tickers)
    #st.write(df_scored.head())

    st.header("Date Picker")
    start_date = st.date_input('Start Date:')
    end_date = st.date_input('End Date:')
    st.header("Overall Sentiment For The Above Date Range")

    if start_date and end_date:

        df_dates = df_scored[(df_scored['date']>=start_date) & (df_scored['date']<=end_date)]
        # st.write(df_dates.tail())
        # Visualization
        for ticker in tickers:
            score = df_scored[df_scored['ticker']==ticker]['compound'].mean()
            if score >= 0.5:
                sent = 'Positive'
            elif score <= -0.5:
                sent = 'Negative'
            else:
                sent = 'Neutral'  
        st.write(ticker,':',sent)

        viz_df = df_scored.groupby(['date','ticker'])['compound'].mean().reset_index()
        viz_df = viz_df[(viz_df['date']>=start_date)&(viz_df['date']<=end_date)]
        viz_df['date'] = viz_df['date'].astype('str')
        viz_df['compound'] = round(viz_df['compound'],2)
        fig = px.line(viz_df, x='date', y='compound', color='ticker', markers=True,color_discrete_sequence=px.colors.qualitative.Antique)
        fig.update_layout( title="Sentiment Score Over Date",xaxis_title="Date",yaxis_title="Sentiment Score",font=dict(size=14))
        st.plotly_chart(fig)
            
    else:
        st.warning('Select Date Range!')

else:
    st.warning('Select 1 or max of 3 companies!')
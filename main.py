import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.subplots as sp

# Set Streamlit app title
st.title('StockWatch Application')

# Create tabs with titles
tabs = st.tabs(["Trending", "Top Trending", "Charts", "Correlation"])

# Trending (get last 1 hour & 1 day trending stocks of nasdaq 100 & nyse 100)
def tab1():
    st.subheader("Top Trending Stocks in last 1 Day")
    
    # read csv and preprocess
    df = pd.read_csv('tweets_with_ticker.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['pos_sentiment'] = 0
    df['neg_sentiment'] = 0
    df['neu_sentiment'] = 0
    df['total'] = 1
    df['pos_sentiment'] = np.where(df['sentiment']=='Positive',1,0)
    df['neu_sentiment'] = np.where(df['sentiment']=='Neutral',1,0)
    df['neg_sentiment'] = np.where(df['sentiment']=='Negative',1,0)
    df['date'] = df['timestamp'].dt.date

    # #### Get last day top 10 trending Tickers on the basis of tweets
    lastdate_df = df[df['date']==df['date'].max()]
    tickers = lastdate_df.groupby('tickers').sum()
    tickers = tickers.reset_index()
    tickers.sort_values(by=['total'], ascending=False,inplace=True, ignore_index=True)
    tb_tickers = tickers
    tickers = tickers.head(10)

    # #### Chart 1 ####
    # Create horizontal bar chart for top 10 trending Tickers on the basis of tweets
    # Define a color scale
    color_scale = px.colors.qualitative.Plotly
    fig = px.bar(tickers, x='total', y='tickers', orientation='h', color='tickers', color_discrete_sequence=color_scale)
    
    # Show the chart in Streamlit
    st.plotly_chart(fig)
    tb_tickers.columns = ['Symbol', 'Positive Sentiment', 'Negative Sentiment', 'Neutral Sentiment', 'Total Tweets']
    
    # #### Chart 2 ####
    # #### Twitter tweets sentiments Analysis part
    st.subheader("Tweets Sentiment for last 1 Day")
    column1, column2 = st.columns(2)

    # count positive, negative and neutral tweets
    sentiment_df = tb_tickers.sum(axis=0)[1:-1]
    sentiment_df = sentiment_df.reset_index()
    sentiment_df.columns =['Sentiment Type', 'Total Tweets']
    
    # Bar chart for positive, negative and neutral tweets
    fig1 = px.bar(sentiment_df, x='Sentiment Type', y='Total Tweets', color='Sentiment Type', color_discrete_sequence=[color_scale[2],color_scale[1],color_scale[0]])
    fig1.update_traces(hovertemplate='Sentiment Type: %{x}<br>Total Tweets: %{y}')  # Specify hover template
    fig1.update_layout(title='Tweets Sentiment Bar Chart')

    # Pie chart for positive, negative and neutral tweets Distribution 
    fig2 = px.pie(sentiment_df, values='Total Tweets', names='Sentiment Type', title='Tweets sentiment Partition Chart')

    # Show the charts in Streamlit App
    column1.plotly_chart(fig1, use_container_width=True,)
    column2.plotly_chart(fig2, use_container_width=True,)
    
    # #### Chart 3 ####
    # #### Check Each Ticker tweets Swentiement
    st.subheader("Tweets Sentiment for Specific Stock Symbol/Ticker")
    symbol_val = st.selectbox("Select Symbol", tb_tickers['Symbol'])
    if symbol_val is not None:
        symbol_tweets_df = tb_tickers[tb_tickers['Symbol']==symbol_val]

        # metrics for tweets
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Tweets", symbol_tweets_df['Total Tweets'])
        col2.metric("Positive Tweets", symbol_tweets_df['Positive Sentiment'], f"{round((symbol_tweets_df['Positive Sentiment'].iloc[0] / symbol_tweets_df['Total Tweets'].iloc[0])*100,0)}%")
        col3.metric("Negative Tweets", symbol_tweets_df['Negative Sentiment'], f"{-1*round((symbol_tweets_df['Negative Sentiment'].iloc[0] / symbol_tweets_df['Total Tweets'].iloc[0])*100,0)}%")
        col4.metric("Neutral Tweets", symbol_tweets_df['Positive Sentiment'], f"{round((symbol_tweets_df['Neutral Sentiment'].iloc[0] / symbol_tweets_df['Total Tweets'].iloc[0])*100,0)}%")

        # count positive, negative and neutral tweets for specific symbol
        symbol_tweets_df = symbol_tweets_df.sum(axis=0)[1:-1]
        symbol_tweets_df = symbol_tweets_df.reset_index()
        symbol_tweets_df.columns =['Sentiment Type', 'Total Tweets']

        # Pie chart for positive, negative and neutral tweets Distribution for specific symbol
        fig3 = px.pie(symbol_tweets_df, values='Total Tweets', names='Sentiment Type', color_discrete_sequence=[color_scale[0],color_scale[2],color_scale[1]])
        fig3.update_layout(title=f'Tweets Sentiment for {symbol_val} Stock')
        fig3.update_traces(textfont_color='white')
        st.plotly_chart(fig3, use_container_width=True)
    
    tb_tickers.columns = ['Symbol', 'Positive Sentiment', 'Negative Sentiment', 'Neutral Sentiment', 'Total Tweets']
    st.subheader("Table of All Symbols with their Tweets Sentiment")
    st.write(tb_tickers)


# Top Trending (get trending stocks for specific hours of day using historical data of nasdaq 100 & nyse 100)
def tab2():
    st.subheader("Top Trending Stocks in an Hour")
    time_val = st.selectbox("Select Hour", ['00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00',
                                            '08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00',
                                            '16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00'], 15)
    time_val = int(time_val.split(':')[0])
    
    # read file and create hour column
    df = pd.read_csv('tweets_with_ticker.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['total'] = 1
    df['hour'] = df['timestamp'].dt.hour
    
    # get data for specific hour on the basis of tweets
    hour_df = df[df['hour']==time_val]
    tickers = hour_df.groupby('tickers').sum()
    tickers = tickers.reset_index()
    tickers.sort_values(by=['total'], ascending=False,inplace=True, ignore_index=True)
    tickers = tickers.head(10)

    # Create horizontal bar chart using Plotly
    color_scale = px.colors.qualitative.Plotly
    fig = px.bar(tickers, x='total', y='tickers', orientation='h', color='tickers', color_discrete_sequence=color_scale)
    
    # Show the chart in Streamlit
    st.plotly_chart(fig)


# Charts (get chart for frequency of no. tweets with sentiment frequency chart (for specific symbol))
def tab3():
    st.subheader("Charts")
    symbol_val = st.text_input("Input Symbol", max_chars=5)
    symbol_val = str.upper(symbol_val)
    df = pd.read_csv('tweets_with_ticker.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['pos_sentiment'] = 0
    df['neg_sentiment'] = 0
    df['neu_sentiment'] = 0
    df['total'] = 1
    df['pos_sentiment'] = np.where(df['sentiment']=='Positive',1,0)
    df['neu_sentiment'] = np.where(df['sentiment']=='Neutral',1,0)
    df['neg_sentiment'] = np.where(df['sentiment']=='Negative',1,0)
    df['date'] = df['timestamp'].dt.date

    tick_chart = df[df['tickers']==symbol_val]
    tick_chart = tick_chart.groupby('date').sum()
    tick_chart = tick_chart.reset_index()
    tick_chart['sentiment'] = np.where(tick_chart['pos_sentiment']>=tick_chart['neg_sentiment'], tick_chart['pos_sentiment'],
                                        -tick_chart['neg_sentiment']) 
    if len(symbol_val)>0:
        st.subheader(f"Daily No. of Tweets of {symbol_val}")
        
        # Create subplots with 2 rows and 1 column, with custom vertical spacing
        fig = sp.make_subplots(rows=2, cols=1, vertical_spacing=0.2)

        # Add first subplot (upper plot)
        fig.add_trace(go.Bar(x=tick_chart['date'], y=tick_chart['total']), row=1, col=1)
        
        # Add second subplot (upper plot)
        fig.add_trace(go.Bar(x=tick_chart['date'], y=tick_chart['sentiment']), row=2, col=1)
        
        # Update subplot titles
        # fig.update_xaxes(title_text='Date', row=1, col=1)
        fig.update_yaxes(title_text='Total No. of Mentions in Tweets', row=1, col=1)
        fig.update_xaxes(title_text='Date', row=2, col=1)
        fig.update_yaxes(title_text='Sentiment', row=2, col=1)

        # Show the chart in Streamlit
        st.plotly_chart(fig)


        st.subheader("Table of all tweets on daily basis with sentiment")
        tick_chart.columns = ['Date', 'Positive Sentiment', 'Negative Sentiment', 'Neutral Sentiment', 'Total Tweets', 'Max(+ve/-ve) Tweets']
        st.write(tick_chart[['Date', 'Positive Sentiment', 'Negative Sentiment', 'Neutral Sentiment', 'Total Tweets']])


# Trending (get stock price chart with no. of tweets cahrt)
def tab4():
    st.subheader("Correlation Chart b/w Stock Price & No. of Mentions in Tweets")
    symbol_val = st.text_input("Input Symbol", max_chars=5, key='tab4')
    symbol_val = str.upper(symbol_val)
    df = pd.read_csv('tweets_with_ticker.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['pos_sentiment'] = 0
    df['neg_sentiment'] = 0
    df['neu_sentiment'] = 0
    df['total'] = 1
    df['pos_sentiment'] = np.where(df['sentiment']=='Positive',1,0)
    df['neu_sentiment'] = np.where(df['sentiment']=='Neutral',1,0)
    df['neg_sentiment'] = np.where(df['sentiment']=='Negative',1,0)
    df['date'] = df['timestamp'].dt.date

    if len(symbol_val)>0:
        tick_chart = df[df['tickers']==symbol_val]
        tick_chart = tick_chart.groupby('date').sum()
        tick_chart = tick_chart.reset_index()
        tick_chart['sentiment'] = np.where(tick_chart['pos_sentiment']>=tick_chart['neg_sentiment'], tick_chart['pos_sentiment'],
                                            -tick_chart['neg_sentiment']) 
        start_date = tick_chart['date'].min()
        end_date = tick_chart['date'].max()

        # Fetch data using yfinance
        stock_data = yf.download(symbol_val, start=start_date, end=end_date)
        st.markdown("### Candlestic Chart Prices Table")
        st.write(stock_data)  

    
        st.subheader(f"Daily No. of Tweets of {symbol_val}")
        
        # Create subplots with 2 rows and 1 column, with custom vertical spacing
        fig = sp.make_subplots(rows=2, cols=1, vertical_spacing=0.2)

        # Add first subplot (upper plot)
        fig.add_trace(go.Candlestick(x=stock_data.index,
                             open=stock_data['Open'],
                             high=stock_data['High'],
                             low=stock_data['Low'],
                             close=stock_data['Close'],
                             name='Candlestick'), row=1, col=1)
        
        # Add second subplot (upper plot)
        fig.add_trace(go.Bar(x=tick_chart['date'], y=tick_chart['sentiment']), row=2, col=1)
        
        # Update subplot titles
        # fig.update_xaxes(title_text='Date', row=1, col=1)
        fig.update_layout(title=f'{symbol_val} Candlestick Chart', xaxis_rangeslider_visible=False)
        fig.update_yaxes(title_text='Total No. of Mentions in Tweets', row=1, col=1)
        fig.update_xaxes(title_text='Date', row=2, col=1)
        fig.update_yaxes(title_text='Sentiment', row=2, col=1)
        # Manually set the range of the x-axis to be the same for both subplots
        x_range = [tick_chart['date'].min(), tick_chart['date'].max()]
        fig.update_xaxes(range=x_range, row=1, col=1)
        fig.update_xaxes(range=x_range, row=2, col=1)

        # Align y-axes of the two subplots based on date
        fig.update_yaxes(overlaying='y', row=2, col=1, secondary_y=True)
        # Show the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)


# Render content for Tab 1
with tabs[0]:
    # Add your content for Tab 1 here
    tab1()

# Render content for Tab 2
with tabs[1]:
    # Add your content for Tab 2 here
    tab2()

# Render content for Tab 3
with tabs[2]:
    # Add your content for Tab 3 here
    tab3()
    
# Render content for Tab 4
with tabs[3]:
    # Add your content for Tab 3 here
    tab4()
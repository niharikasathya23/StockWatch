import pandas as pd
from textblob import TextBlob
import numpy as np
import re
import schedule
import time

#Define the sentiment_analysis function
def sentiment_analysis(tweet):
    analysis = TextBlob(tweet)
    sentiment = analysis.sentiment.polarity

    if sentiment > 0:
        return 'Positive'
    elif sentiment == 0:
        return 'Neutral'
    else:
        return 'Negative'
    
def main():
    df = pd.read_csv('Tweets.csv')
    df.drop_duplicates(inplace=True, ignore_index=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Apply sentiment_analysis function on 'tweets' column
    df['sentiment'] = df['tweets'].apply(sentiment_analysis)

    # Print sentiment analysis results
    sentiment_counts = df['sentiment'].value_counts()
    total_tweets = len(df)
    positive_percentage = (sentiment_counts['Positive'] / total_tweets) * 100
    neutral_percentage = (sentiment_counts['Neutral'] / total_tweets) * 100
    negative_percentage = (sentiment_counts['Negative'] / total_tweets) * 100

    print('Sentiment Analysis Results:')
    print('Total Tweets: {}'.format(total_tweets))
    print('Positive Tweets: {:.2f}%'.format(positive_percentage))
    print('Neutral Tweets: {:.2f}%'.format(neutral_percentage))
    print('Negative Tweets: {:.2f}%'.format(negative_percentage))
    print('Neutral Tweets: {:.2f}%'.format(neutral_percentage))


    # ns100_df = pd.read_csv('nasdaq100.csv')
    # symbol_list = ns100_df['Symbols'].to_list()
    ns_df = pd.read_csv('nasdaq-listed-symbols.csv')
    nyse_df = pd.read_csv('nyse-listed_csv.csv')
    symbol_list = ns_df['Symbol'].to_list() + nyse_df['ACT Symbol'].to_list()
    symbol_count = {} # Dictionary to store symbol counts
    symbol_list

 # # define the pattern to extract the tickers
    pattern = r'\b(?:' + '|'.join(map(re.escape, symbol_list)) + r')\b'

    # extract the tickers from tweets column and store them in a new column
    df['tickers'] = df['tweets'].str.findall(pattern).apply(lambda x: list(set(x)))

    # drop rows with empty tickers
    df = df[df['tickers'].apply(lambda x: len(x) > 0)]

    # explode tickers column into multiple rows
    df = df.explode('tickers', ignore_index=True)

    df.to_csv('tweets_with_ticker.csv', index=False)
   


if __name__=='__main__':
    # Schedule the main() function to run every minute
    schedule.every().hour.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
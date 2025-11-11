import pandas as pd
from textblob import TextBlob
import numpy as np
import re
import schedule
import time
import boto3
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Mongodb settings
mongo_password = os.getenv('MONGO_PASSWORD')
mongo_user = os.getenv('MONGO_USER')
uri = f"mongodb+srv://{mongo_user}:{mongo_password}@cluster0.ejkrmrs.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Provide your AWS access key and secret access key
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# Specify the S3 bucket name and file key
bucket_name = 'stock-market-kafka-project-asra1'
csv_list=[]
temp_folder='temp_data_folder'

try:
    # Create an S3 client
    s3 = boto3.resource('s3',
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)
except Exception as e:
    print(e)


def read_files_bucket(s3=None):
    # Get the bucket object
    bucket = s3.Bucket(bucket_name)

    # List all objects in the bucket
    for obj in bucket.objects.all():
        if '.csv' in str(obj.key)[4:]:
            csv_list.append(obj.key)

    # create temp folder and store files get from bucket
    if os.path.exists(temp_folder):
        pass
    else:
        os.mkdir(temp_folder)
    
    # store data in file
    for c,i in enumerate(csv_list):
        # Download the file from S3 to a local file
        bucket.download_file(i, temp_folder+'\\'+f'temp{c}.csv')
        df=pd.read_csv(temp_folder+'\\'+f'temp{c}.csv')
        if os.path.exists(temp_folder+'\\tweets.csv'):
            df.to_csv(temp_folder+'\\tweets.csv', index=False)
        else:
            df.to_csv(temp_folder+'\\tweets.csv', index=False, mode='a', header=False)
        os.remove(temp_folder+'\\'+f'temp{c}.csv')
    



# Define the sentiment_analysis function
def sentiment_analysis(tweet):
    analysis = TextBlob(tweet)
    sentiment = analysis.sentiment.polarity

    if sentiment > 0:
        return 'Positive'
    elif sentiment == 0:
        return 'Neutral'
    else:
        return 'Negative'
    
def main(s3):
    if s3:
        read_files_bucket(s3)
        df = pd.read_csv(temp_folder+'\\tweets.csv')
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

        # ns100_df = pd.read_csv('nasdaq100.csv')
        # symbol_list = ns100_df['Symbols'].to_list()
        ns_df = pd.read_csv('nasdaq-listed-symbols.csv')
        nyse_df = pd.read_csv('nyse-listed_csv.csv')
        symbol_list = ns_df['Symbol'].to_list() + nyse_df['ACT Symbol'].to_list()
        symbol_count = {} # Dictionary to store symbol counts
        symbol_list


        # define the pattern to extract the tickers
        pattern = r'\b(?:' + '|'.join(map(re.escape, symbol_list)) + r')\b'

        # extract the tickers from tweets column and store them in a new column
        df['tickers'] = df['tweets'].str.findall(pattern).apply(lambda x: list(set(x)))

        # drop rows with empty tickers
        df = df[df['tickers'].apply(lambda x: len(x) > 0)]

        # explode tickers column into multiple rows
        df = df.explode('tickers', ignore_index=True)

        df.to_csv('tweets_with_ticker.csv', index=False)
        data = df.to_dict(orient='records')
        db = client['TWEETS_DB']
        db.tweet_tb.insert_many(data)


if __name__=='__main__':
    # Schedule the main() function to run every minute
    schedule.every().hour.do(main,s3)
    while True:
        schedule.run_pending()
        time.sleep(1)
    
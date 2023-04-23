import tweepy
import time
import pandas as pd
import schedule
from kafka import KafkaProducer
from json import dumps
import boto3
import os
from datetime import datetime

server_public_ip = '13.52.102.20:9092'
try:
    producer = KafkaProducer(bootstrap_servers=[server_public_ip],
                            value_serializer=lambda x:
                            dumps(x).encode('utf-8'))
except Exception as e:
    print(e)  

# Set up Twitter API credentials
consumer_key = 'cJEqEEK4vqFPsqEAaIphipZ3q'
consumer_secret = '8BwWie7Vqjm9qQuAAErYXHkNNm5Xc5NH89gumymDYtf7lnXIcF'
access_token = '1187325630678892545-SQ9i3KpIUZSYrK6V7NC6UFFLqjEZIa'
access_token_secret = 'sZeApBzOXXeRXlpTiEGewIvMC6TH9dq8LXOBIgvhYgUpD'

# Authenticate to Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

try:
    # Create API object
    api = tweepy.API(auth)
except Exception as e:
    print(e)  

# Provide your AWS access key and secret access key
aws_access_key_id = 'YOUR_AWS_KEY'
aws_secret_access_key = 'YOUR_AWS_SECRET'
# Create an S3 client with credentials
try:
    s3 = boto3.resource('s3',
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)
except Exception as e:
    print(e)    

# Function to store tweets in a CSV file
def store(tweets_time_list=[], tweets_list=[]):
    # global producer
    global s3
    df = pd.DataFrame({'timestamp':tweets_time_list,'tweets':tweets_list})
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.drop_duplicates(inplace=True)
    df.to_csv('Tweets.csv', index=False, mode='a', header=False)  # Updated: set header=False
    df.to_csv('temp_Tweets.csv', index=False)
    timestamp = datetime.now()
    s3.meta.client.upload_file("temp_Tweets.csv",
                           'stock-market-kafka-project-asra1',
                           f'tweets_{timestamp}.csv')
    os.remove('temp_Tweets.csv')
    print(len(df))
    ## Send Data to Consumer
    # df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))  # Convert Timestamp to string
    # records = df.to_dict(orient='records')
    # for record in records:  
    #     producer.send('demo_testing2', value=record)


# Function to get tweets from twitter and store them in CSV file
def main(api=None, no_tweets=100, search_query=[]):
    try:
        for i in search_query:
            tweets_list=[]
            tweets_time_list=[]

            # Fetch tweets using Tweepy
            tweets = tweepy.Cursor(api.search_tweets, q=i, tweet_mode='extended').items(100)

            for i in tweets: 
                tweets_list.append(i._json['full_text'])
                tweets_time_list.append(i._json['created_at'])
            store(tweets_time_list, tweets_list)
            print("Working")
            time.sleep(15)
            
    except Exception as e:
        print(e)
        store(tweets_time_list, tweets_list)


if __name__=='__main__':
    # Define search query and number of tweets to fetch
    search_query = ['#nasdaq', '$nasdaq', '#nyse',
                    '$nyse', '#stockmart', '#cashtag',
                    '$nasdaq100','$nyse100','#nasdaq100',
                    '#nyse100']
    
    # Schedule the function to run every hour
    schedule.every().hour.do(main, api, 100, search_query)
    while True:
        schedule.run_pending()
        time.sleep(1)
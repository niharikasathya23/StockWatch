import tweepy
import time
import pandas as pd
import schedule
from kafka import KafkaProducer
from json import dumps
# producer = KafkaProducer(bootstrap_servers=['13.52.102.20:9092'],
#                          value_serializer=lambda x:
#                          dumps(x).encode('utf-8'))

# Set up Twitter API credentials
consumer_key = 'cJEqEEK4vqFPsqEAaIphipZ3q'
consumer_secret = '8BwWie7Vqjm9qQuAAErYXHkNNm5Xc5NH89gumymDYtf7lnXIcF'
access_token = '1187325630678892545-SQ9i3KpIUZSYrK6V7NC6UFFLqjEZIa'
access_token_secret = 'sZeApBzOXXeRXlpTiEGewIvMC6TH9dq8LXOBIgvhYgUpD'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Create API object
api = tweepy.API(auth)

if __name__=='__main__':
    # Define search query and number of tweets to fetch
    search_query = ['#nasdaq','$nasdaq', '#nyse','$nyse','#stockmart','#cashtag','$nasdaq100','$nyse100','#nasdaq100','#nyse100']
    
    # Schedule the function to run every hour
    schedule.every().hour.do(main, api, 100, search_query)
    while True:
        schedule.run_pending()
        time.sleep(1)
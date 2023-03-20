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
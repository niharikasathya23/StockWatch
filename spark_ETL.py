# libraries
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, split, length, explode, regexp_replace
from pyspark.sql.types import StringType, FloatType
from textblob import TextBlob
import re
import boto3
import pandas as pd
import os
import schedule
import time
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
    for i in csv_list:
        # Download the file from S3 to a local file
        bucket.download_file(i, temp_folder+'/'+i)
        df=pd.read_csv(temp_folder+'/'+i)
        if os.path.exists(temp_folder+'/tweets.csv'):
            df.to_csv(temp_folder+'/tweets.csv', index=False)
        else:
            df.to_csv(temp_folder+'/tweets.csv', index=False, mode='a', header=False)
        os.remove(temp_folder+'/'+i)
    

def ETL():
    # Create a Spark session
    spark = SparkSession.builder.appName("SentimentAnalysis").getOrCreate()

    # Read the CSV file into a PySpark DataFrame
    df = spark.read.csv(temp_folder+'/tweets.csv', header=True)

    # Drop duplicates from the DataFrame
    df = df.dropDuplicates()

    # Remove Null rows
    df = df.dropna()

    # Convert the 'timestamp' column to a timestamp data type
    df = df.withColumn("timestamp", col("timestamp").cast("timestamp"))

    # Define a user-defined function (UDF) for sentiment analysis
    def sentiment_analysis(tweet):
        if tweet is not None:
            analysis = TextBlob(tweet)
            sentiment = analysis.sentiment.polarity

            if sentiment > 0:
                return 'Positive'
            elif sentiment == 0:
                return 'Neutral'
            else:
                return 'Negative'
        else:
            return None

    # Register the UDF with Spark
    sentiment_analysis_udf = udf(sentiment_analysis, StringType())

    # Apply the UDF on the 'tweets' column and create a new 'sentiment' column
    df = df.withColumn("sentiment", sentiment_analysis_udf(col("tweets")))

    # Calculate sentiment analysis results
    sentiment_counts = df.groupBy("sentiment").count().collect()
    total_tweets = df.count()
    positive_percentage = (sentiment_counts[0]["count"] / total_tweets) * 100
    neutral_percentage = (sentiment_counts[1]["count"] / total_tweets) * 100
    negative_percentage = (sentiment_counts[2]["count"] / total_tweets) * 100

    # Print sentiment analysis results
    print('Sentiment Analysis Results:')
    print('Total Tweets: {}'.format(total_tweets))
    print('Positive Tweets: {:.2f}%'.format(positive_percentage))
    print('Neutral Tweets: {:.2f}%'.format(neutral_percentage))
    print('Negative Tweets: {:.2f}%'.format(negative_percentage))

    # Read the symbol lists into PySpark DataFrames
    ns_df = spark.read.csv('nasdaq-listed-symbols.csv', header=True)
    nyse_df = spark.read.csv('nyse-listed_csv.csv', header=True)

    # Extract tickers from 'tweets' column using regular expressions and store them in a new column 'tickers'
    symbol_list = ns_df.select("Symbol").rdd.flatMap(lambda x: x).collect() + nyse_df.select("ACT Symbol").rdd.flatMap(lambda x: x).collect()
    pattern = r'\b(?:' + '|'.join(map(re.escape, symbol_list)) + r')\b'
    extract_tickers_udf = udf(lambda tweet: re.findall(pattern, str(tweet)), StringType())  # Convert tweet to string
    df = df.withColumn("tickers", extract_tickers_udf(col("tweets")))

    # remove empty list rows
    df = df.withColumn("tweets_length", length(col("tickers")))
    df = df.filter(df.tweets_length >= 3)
    df = df.drop("tweets_length")

    # Convert "tickers" column from string type to array type
    df = df.withColumn("tickerss", split("tickers", ","))

    # Explode "tickers" column to separate rows
    df = df.selectExpr("*", "explode(tickerss) as ticker")

    df = df.drop("tickerss")

    # Remove '[' and ']' from the "ticker" column
    df = df.withColumn("tickers", regexp_replace("ticker", r"[\[\]]", ""))
    df = df.drop("ticker")

    df.write.csv("tweets_with_ticker", header=True, mode="overwrite")
    files_c = os.listdir("tweets_with_ticker")
    for i in files_c:
        if '.csv' in i[-4:]:
          dd=pd.read_csv('tweets_with_ticker/'+i, error_bad_lines=False)
    data = dd.to_dict(orient='records')
    db = client['TWEETS_DB']
    db.tweet_tb.insert_many(data)


def main(s3):
    if s3:
        read_files_bucket(s3)
        ETL()

if __name__=='__main__':
    # Schedule the main() function to run every minute
    schedule.every().hour.do(main,s3)
    while True:
        schedule.run_pending()
        time.sleep(1)
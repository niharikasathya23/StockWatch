from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType, FloatType
from textblob import TextBlob
import re

# Create a Spark session
spark = SparkSession.builder.appName("SentimentAnalysis").getOrCreate()

# Read the CSV file into a PySpark DataFrame
df = spark.read.csv("Tweets.csv", header=True)

# Drop duplicates from the DataFrame
df = df.dropDuplicates()

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

# Print sentiment analysis results
print('Sentiment Analysis Results:')
print('Total Tweets: {}'.format(total_tweets))


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
extract_tickers_udf = udf(lambda tweet: re.findall(pattern, tweet), StringType())
df = df.withColumn("tickers", extract_tickers_udf(col("tweets")))

# Drop rows with empty tickers
df = df.filter(col("tickers").isNotNull())

# Explode the 'tickers' column into multiple rows
df = df.select("timestamp", "tweets", "sentiment", "tickers").explode("tickers", "ticker")

# Write the result to a CSV file
df.write.csv("tweets_with_ticker.csv", header=True, mode="overwrite")

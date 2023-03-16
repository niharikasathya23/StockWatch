from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType, FloatType
from textblob import TextBlob
import re

# Create a Spark session
spark = SparkSession.builder.appName("SentimentAnalysis").getOrCreate()

# Read the CSV file into a PySpark DataFrame
#df = spark.read.csv("Tweets.csv", header=True)


# Register the UDF with Spark
sentiment_analysis_udf = udf(sentiment_analysis, StringType())

# Apply the UDF on the 'tweets' column and create a new 'sentiment' column

# Print sentiment analysis results
# print('Sentiment Analysis Results:')
# print('Total Tweets: {}'.format(total_tweets))
# print('Positive Tweets: {:.2f}%'.format(positive_percentage))
#print('Neutral Tweets: {:.2f}%'.format(neutral_percentage))
#print('Negative Tweets: {:.2f}%'.format(negative_percentage))

# Read the symbol lists into PySpark DataFrames
ns_df = spark.read.csv('nasdaq-listed-symbols.csv', header=True)
nyse_df = spark.read.csv('nyse-listed_csv.csv', header=True)

# Extract tickers from 'tweets' column using regular expressions and store them in a new column 'tickers'
symbol_list = ns_df.select("Symbol").rdd.flatMap(lambda x: x).collect() + nyse_df.select("ACT Symbol").rdd.flatMap(lambda x: x).collect()
pattern = r'\b(?:' + '|'.join(map(re.escape, symbol_list)) + r')\b'
extract_tickers_udf = udf(lambda tweet: re.findall(pattern, tweet), StringType())

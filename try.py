print("hello Nishee")
print("hfkkgnvd,bih,ffnjbjhet")
def sentiment_analysis(tweet):
    analysis = TextBlob(tweet)
    sentiment = analysis.sentiment.polarity

    if sentiment > 0:
        return 'Positive'
    elif sentiment == 0:
        return 'Neutral'
    else:
        return 'Negative'
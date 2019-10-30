# -*- coding: utf-8 -*-
import csv
import re
import string
import sys
import tweepy

#### Application credentials
consumer_key = 'hr7r1frxR7reyi9L6DcWSnOIK'
consumer_secret = 'KyWUrbxJyseVDtnzwTMDDHqRzajTsZtvkcoIjQeFhAcaadZ8wf'
access_token = '341949863-C1YQ0pIkVStn0xFHZ5CSmui9LPFrz5xeF3dIiPvH'
access_token_secret = 'dPszVmB5TXjVQ8yQHu0WQDyIeHu3bUTe7dwKI9LE0mZGC'

## Application handler
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

## Usage command line
if (len(sys.argv) != 2):
  print("Usage: python test.py <keyword for sentiment analysis>")
  exit()

#### Search Twitter and make a list of matching tweets
tweetList = []
COUNT_TWEETS = 2000
for tweet in tweepy.Cursor(api.search,
                           q=sys.argv[1],
                           result_type="recent",
                           count=100,
                           tweet_mode="extended",
                           lang="en").items(COUNT_TWEETS):
    ttext = tweet.full_text
    if hasattr(tweet, 'retweeted_status'):
        ttext = tweet.retweeted_status.full_text
    tweetList.append(ttext.encode('utf-8'))

if (len(tweetList) < COUNT_TWEETS/2):
  print("Not enough tweets to compute a score.")
  exit();

### Preprocess tweets
def processTweet2(tweet):
    #Convert to lower case
    tweet = tweet.lower().decode('utf-8')
    #Remove www.* or https?://*
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',tweet)
    #Remove @username
    tweet = re.sub('@[^\s]+','',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #trim
    tweet = tweet.strip('\'"')
    tweet = tweet.translate(string.punctuation)
    return tweet    


### Load from file and build a list
def loadFromFile(wordListFileName):
    #read the file and build a list
    words = []

    fp = open(wordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        word = word.lower()
        words.append(word)
        line = fp.readline()
    fp.close()
    return words


positiveWords = loadFromFile('positive_words.txt')
negativeWords = loadFromFile('negative_words.txt')
notWords = ["not", "never"]


def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
#end


def getSentiment(tweet):
    positive_sentiment = 0;
    negative_sentiment = 0;
    not_sentiment = 0;

    #split tweet into words
    words = tweet.split()
    for w in words:
        #replace two or more with two occurrences
        w = replaceTwoOrMore(w)
        #strip punctuation
        w = w.strip('\'"?,.')
        #check if the word stats with an alphabet
        val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)

        #look for sentiment words
        if (w in positiveWords):
          if (not_sentiment>0):
            negative_sentiment = negative_sentiment + 1
            not_sentiment = not_sentiment - 1
            #print("negative word = " + w)
          else:
            positive_sentiment = positive_sentiment + 1
            #print("positive word = " + w)
        if (w in negativeWords):
          if (not_sentiment>0):
            positive_sentiment = positive_sentiment + 1
            #print("positive word = " + w)
            not_sentiment = not_sentiment - 1
          else:
            negative_sentiment = negative_sentiment + 1
            #print("negative word = " + w)
        if (w in notWords): not_sentiment = not_sentiment + 1

    sentiment = (positive_sentiment - negative_sentiment)
    return sentiment;
 

count_tweets = 0.0
positive_tweets = 0
negative_tweets = 0

## load twitter data and compute the overall sentiment 
for line in tweetList:
    processedTweet = processTweet2(line)
    sentiment = getSentiment(processedTweet)
    if (sentiment > 0): positive_tweets = positive_tweets + 1;
    if (sentiment < 0): negative_tweets = negative_tweets + 1;
    if (sentiment != 0):
      print("Tweet = " + str(line))
      print("Sentiment = " + str(sentiment))
      print
    count_tweets = count_tweets + 1.0;

print("Positive tweets = " + str(positive_tweets))
print("Negative tweets = " + str(negative_tweets))
print("Overall counts = " + str(count_tweets))

## Compute the final score
print("Twitter sentiment score = " + str(100 * positive_tweets/count_tweets * (1-negative_tweets/count_tweets) * (1-negative_tweets/count_tweets)))
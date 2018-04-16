import pandas as pd
import preprocessor as p
from nltk.tokenize import TweetTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class DailySentiment:
    def __init__(self):
        # instantiate tweet tokenizer from nltk.tokenize, set to remove handles and reduce repeating characters
        self._tweetProcessor = TweetTokenizer(strip_handles=False, reduce_len=True)
        # instantiate sentiment intensity analyzer from nltk.sentiment.vader
        self._vaderAnalyzer = SentimentIntensityAnalyzer()
    
    # External function to return average VADER polarity score
    # getDailySentiment(df = dataframe, keyword = string, filterTweets = boolean, noninfluence = boolean)
    # keyword: search term tweets were queried with
    # filterTweets and noninfluence: booleans to run/skip particular preprocessing function
    def getDailySentiment(self, df, keyword=None, filterTweets=True, noninfluence=True):
        scores = self.getSentimentScores(df, keyword, filterTweets, noninfluence)
        
        avg_scores = {'neg': sum(score['neg'] for score in scores) / len(scores),
                      'neu': sum(score['neu'] for score in scores) / len(scores),
                      'pos': sum(score['pos'] for score in scores) / len(scores),
                      'compound': sum(score['compound'] for score in scores) / len(scores)}
        return avg_scores
    
    # External function to return a list of VADER polarity scores
    # getSentimentScores(df = dataframe, keyword = string, filterTweets = boolean, noninfluence = boolean)
    # keyword: search term tweets were queried with
    # filterTweets and noninfluence: booleans to run/skip particular preprocessing function
    def getSentimentScores(self, df, keyword=None, filterTweets=True, noninfluence=True):
        if (filterTweets or keyword != None):
            df = self._filterTweets(df, keyword)
        if noninfluence:
            df = self._removeNoninfluencers(df)
        
        list_of_tweets = df.text
        scores = []
        for tweet in list_of_tweets:
            tweet = self._cleanTweet(tweet)
            scores.append(self._vaderAnalyzer.polarity_scores(tweet))
        return scores        
    
    # Internal function to remove tweets without keyword (BUG FIX)
    # _filterTweets(df = dataframe, keyword = string)
    def _filterTweets(self, df, keyword):
        df_filtered = df[df.text.str.contains(keyword)]
        return df_filtered
        
    # Internal function to remove tweets from users below a follower threshold
    # _removedNoninfluencers(df = dataframe, min_follower = int <-defaulted to 100)
    def _removeNoninfluencers(self, df, min_follower = 100):
        df_filtered = df[df.user_followers_count > min_follower]
        return df_filtered
    
    # Internal function that goes through several text preprocessing steps
    # _cleanTweet(tweet = string)
    def _cleanTweet(self, tweet):
        # set preprocessor to remove links, mentions, and reserved words (FAV, RT, etc.)
        p.set_options(p.OPT.URL, p.OPT.MENTION, p.OPT.RESERVED)
        # clean tweet with preprocessor and remove hashtags
        tweet = p.clean(tweet.translate(None, "#"))

        return tweet 
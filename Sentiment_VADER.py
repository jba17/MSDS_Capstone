import pandas as pd
import preprocessor as p
from nltk.tokenize import TweetTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json
import csv
import os
import re

class DailySentiment:
    def __init__(self, crypto, folder):
        # instantiate tweet tokenizer from nltk.tokenize, set to remove handles and reduce repeating characters
        self._tweetProcessor = TweetTokenizer(strip_handles=False, reduce_len=True)
        # instantiate sentiment intensity analyzer from nltk.sentiment.vader
        self._vaderAnalyzer = SentimentIntensityAnalyzer()
        
        self.crypto = crypto
        self.folder = folder
    
    # ---- OBSOLETE FUNCTION BELOW ---- UNSUPPORTED: DO NOT USE
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
    # ---- OBSOLETE FUNCTION ABOVE ---- UNSUPPORTED: DO NOT USE
    
    # External function to write csv files of VADER sentiment scores across tweet files in object given folder
    def compileSentiments(self):
        # get list of daily tweet files in folder 
        files = self._getRawFiles()
        # loop through each folder and save csv
        for filename in files:
            df = self._openTweets(filename)
            
            if self.folder == 'csv_daily':
                scores = self.getSentimentScores(df, keyword=self.crypto)
            else:
                scores = self.getSentimentScores(df, keyword=self.crypto, noninfluence=False)
            self._writeSentiment(filename, scores)
            
    
    # External function to return a list of VADER polarity scores
    # getSentimentScores(df = dataframe, keyword = string, filterTweets = boolean, noninfluence = boolean)
    # keyword: search term tweets were queried with
    # filterTweets and noninfluence: booleans to run/skip particular preprocessing function
    def getSentimentScores(self, df, keyword=None, filterTweets=True, noninfluence=True):
        if (filterTweets and keyword != None):
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
        if keyword == 'Bitcoin':
            df_filtered = df[(df.text.str.contains(keyword, case=False))]
        else:
            df_filtered = df[df.text.str.contains(keyword, case=False)]
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
        # clean tweet with preprocessor and remove unwanted symbols (hashtags, quotes, question marks)
        tweet = p.clean(tweet.translate(None, '#?"'))

        return tweet 
    
    # Internal function that opens .txt containing tweets in object given folder
    # _openTweets(filename = string)    
    def _openTweets(self, filename):
        # construct folder path where files reside
        if self.folder == 'csv_daily':
            path = 'data/' + self.folder + '/' + self.crypto + '/' + filename
            df = pd.read_csv(path, lineterminator='\n')
        else:
            path = 'data/' + self.folder + '/' + '/' + filename
            lines = open(path,'r').read().split('\n')
            df = pd.DataFrame(data={'text':lines})      
                
        return df
        
    # Internal function that writes .txt containing VADER sentiment results for each tweet
    # _writeSentiment(filename = string)
    def _writeSentiment(self, filename, scores):
        # construct folder path where files to be written
        path = 'data/VADER/' + self.folder + '/' + self.crypto + '/' + filename
        
        with open(path, 'w') as outfile:
            rowWriter = csv.writer(outfile)       
            # write header
            rowWriter.writerow(['compound', 'neg', 'neu', 'pos'])
        
            for score in scores:
                rowWriter.writerow([score['compound'], score['neg'], score['neu'], score['pos']])
            outfile.close()
        
    # Internal function extracting list of csv files in folder
    # _getRawFiles(folder = string)
    def _getRawFiles(self):
        # construct folder path where files reside
        if self.folder == 'csv_daily':
            path = str(os.getcwd()) + '/data/' + self.folder + '/' + self.crypto
        else:
            path = str(os.getcwd()) + '/data/' + self.folder
                    
        # using regex expression to only take file_names (instead of full paths)
        reg = re.compile("\d{8}")
            
        # loop to generate list of all files in folder that fit naming convention
        files = []
        for csv_path in os.listdir(path):
            if reg.search(csv_path):
                 files.append(csv_path)
        return files
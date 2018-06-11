#!/anaconda3/bin/python

# coding: utf-8

# # Importing Libraries

# In[1]:


import tweepy
import pandas as pd
import numpy as np
import os
from tweepy import OAuthHandler
import csv
import matplotlib.pyplot as plt

pd.options.display.max_columns = 50
pd.options.display.max_rows= 50
pd.options.display.width= 120


# In[2]:


os.chdir("data/Capstone/Data_Extraction")


# # Authentication

# In[3]:


def load_api():
    ''' Function that loads the twitter API after authorizing the user. '''

    consumer_key = 'Key'
    consumer_secret = 'Secret'
    access_token = 'Token'
    access_secret = 'Secret'
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    # load the twitter API via tweepy
    return tweepy.API(auth)


api = load_api()


results=api.search(q='Bitcoin')



# ## Loop



results = []
for tweet in tweepy.Cursor(api.search, q="Bitcoin",lang='en').items(1500):
    results.append(tweet)

print(len(results))








# ## Store as CSV

def process_results(results):
    id_list = [tweet.id for tweet in results]
    data_set = pd.DataFrame(id_list, columns=["id"])

    # Processing Tweet Data

    data_set["text"] = [tweet.text for tweet in results]
    data_set["created_at"] = [tweet.created_at for tweet in results]
    data_set["retweet_count"] = [tweet.retweet_count for tweet in results]
    data_set["favorite_count"] = [tweet.favorite_count for tweet in results]
    data_set["source"] = [tweet.source for tweet in results]

    # Processing User Data
    data_set["user_id"] = [tweet.author.id for tweet in results]
    data_set["user_screen_name"] = [tweet.author.screen_name for tweet in results]
    data_set["user_name"] = [tweet.author.name for tweet in results]
    data_set["user_created_at"] = [tweet.author.created_at for tweet in results]
    data_set["user_description"] = [tweet.author.description for tweet in results]
    data_set["user_followers_count"] = [tweet.author.followers_count for tweet in results]
    data_set["user_friends_count"] = [tweet.author.friends_count for tweet in results]
    data_set["user_location"] = [tweet.author.location for tweet in results]

    return data_set
data_set = process_results(results)

os.chdir("data/Data_Extraction/Bitcoin/")

import time
timestr = time.strftime("%Y%m%d-%H%M%S")

data_set.to_csv("Bitcoin"+timestr+".csv")

print("Task completed at {}".format(timestr))

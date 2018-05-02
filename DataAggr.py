# Purpose of program is to generate dataframes to use for analysis from 
# multiple saved csv files during other python programs.  Functions are
# used to consolidate script in jupyter notebook used for analysis.
# Files are taken from a predetermined folder structure as mapped out in
# www.github.com/JackNelson/Capstone
import pandas as pd
import os
import re
from datetime import datetime

# External function to return a dataframe of VADER polarity scores from multiple VADER result csv files
# fetchSentiments(folder = string, crypto = string)
# folder and crypto: levels of detail in predetermined folder structure used to path to pull files
def fetchSentiments(folder, crypto):
    reg = re.search('\d{8}')
    path = 'data/VADER/' + folder + '/' + crypto
    #create list of .txt files in folder path that match regular expression
    files = [reg.search(filename).group(0) for filename in os.listdir(path) if reg.search(filename)]
    
    #initialize and append dataframes made from each .txt file
    for filename in files:
        df_exists = 'df' in locals() or 'df' in globals()
            if not df_exists:
                df = pd.read_csv(path+filename+'.txt')
                df['date'] = datetime.strptime(filename, '%Y%m%d')
            else:
                temp = pd.read_csv(path+filename+'.txt')
                temp['date'] = datetime.strptime(filename, '%Y%m%d')
                df = pd.concat([df, temp])                
    return df

# External function to return a dataframe of the highest VADER polarity score between pos/neg in VADER score df
# getPolarity(df = pd.DataFrame)   
def getPolarity(df):
    data = {'date':[], 'value':[], 'variable':[]}
    for index, row in df.iterrows():
        data['date'].append(row['date'])
        if row['pos'] > row['neg']:
            data['value'].append(row['pos'])
            data['variable'].append('pos')
        else:
            data['value'].append(row['neg']*-1)
            data['variable'].append('neg')
    df_polarity = pd.DataFrame.from_dict(data)
    
    return df_polarity


# External function to return a dataframe of daily price changes from CoinAPI OCHLV csv file
# getPriceDiff(df = pd.DataFrame)    
def getPriceDiff(df):
    data = {'date':[], 'price_diff':[]}
    for index, row in df.iterrows():
        data['date'].append(datetime.strptime(row['date'], '%Y-%m-%dT%H:%M:%S.%fZ'))
        data['price_diff'].append(row['price_close'] - row['price_open'])
    df_price_diff = pd.DataFrame.from_dict(data)
    
    return df_price_diff
        
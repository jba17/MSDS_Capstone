# Purpose of program is to use coinAPI to pull information about certain cryptocurrencies
# using the REST portion of coinAPI.io.  Various functions within the class can also
# open and save coinAPI.io response objects for later use.  Files are saved in a 
# predetermined folder structure as mapped out in www.github.com/JackNelson/Capstone 
import dateutil
import json
import requests
from googletrans import Translator

# Custom exception handling for non-successful http requests to coinAPI.io (status_code != 200)
class UnsuccessfulRequest(Exception):
        def __init__(self, status_code):
            responses = {400 : "Bad Request - Undetermined error", 401 : "Unauthorized - Incorrect API key", 
                         403 : "Forbidden - Insufficient privileges", 429 : "Rate Limit - Over daily request limit", 
                         550 : "No Data - Data requested unavailable"}
            
            self.status_code = status_code
            self.status_response = responses.get(int(status_code))
            
            self.translator = Translator()

class CoinAPI:
    def __init__(self, key):
        # set headers and url stem used for all requests within coinAPI
        self.key = key
        self.headers = {'X-CoinAPI-Key' : self.key}
        self._url_stem = 'https://rest.coinapi.io/v1'
        
        # initializing request limits for specific API Key - defaults to Free API Key Limits 
        self.request_limits = {'X-RateLimit-Limit': 100, 'X-RateLimit-Remaining': 100, 
                               'X-RateLimit-Request-Cost' : 0, 'X-RateLimit-Reset' : None}
       
    # External function that returns historical OHLCV information related to a specific cryptocurrency
    # getHistOHLCV(symbol_id = string, period_id = string, time_start = string, time_end = string, limit = int)
    # period_id defaulted to 1DAY, reference coinAPI documentation for full list of period_ids
    # end_time optional, defaulted to None, request will pull tweets at start in chronological order until limit reached
    # limit optional, defaulted to 100, each multiple of 100 counts as a request with the coinAPI interface
    # times follow ISO 8601 time format (YYY-MM-DDThh:mm:ss)
    def getHistOHLCV(self, symbol_id, time_start, period_id='1DAY', time_end=None, limit=100):
        if time_end == None:
            url = self._url_stem+'/ohlcv/'+symbol_id+'/history?period_id='+period_id+'&time_start='+time_start+'&limit='+str(limit)
        else:
            url = self._url_stem+'/ohlcv/'+symbol_id+'/history?period_id='+period_id+'&time_start='+time_start+'&time_end='+time_end+'&limit='+str(limit)           
        response_object = requests.get(url, headers=self.headers)
        
        self._responseCheck(response_object)
        self._updateRequestLimits(response_object)
        # returning only the tweet objects within REST API response object
        return json.loads(response_object.text)
        
    # Internal function that writes .txt containing VADER sentiment results for each tweet
    # _writeSentiment(filename = string)
    def _writeHistOHLCV(self, filename, prices):
        # construct folder path where files to be written
        path = 'data/price_data/' + filename
        
        with open(path, 'w') as outfile:
            rowWriter = csv.writer(outfile)       
            # write header
            rowWriter.writerow(['time_close', 'trades_count', 'volume_traded', 'time_period_start', 'time_period_end', 
                                'price_close', 'price_high', 'time_open', 'price_open', 'price_low'])
        
            for price in prices:
                rowWriter.writerow([price['time_close'], price['trades_count'], price['volume_traded'], price['time_period_start'], 
                                    price['time_period_end'], price['price_close'], price['price_high'], price['time_open'], 
                                    price['price_open'], price['price_low']])
            outfile.close()
    
    # External function that loops through historical tweets function and returns list of tweets
    # loopHistTweets(time_start = string, loops = int, gap = int)
    # loops optional, defaulted to 24, number of iterations, default set to 100 tweets per hour for 24 hours
    # gap optional, defaulted to 60, minutes between time_start iterations
    # time_start follows ISO 8601 time format (YYYY-MM-DDThh:mm:ss)
    def loopHistTweets(self, time_start, loops=24, gap=60):
        list_hist_tweet_objects = []
        
        for i in range(loops):
            hist_tweet_object = {}
            # convert string to datetime, add gap time, convert back to string
            start_date = dateutil.parser.parse(time_start)
            start_date += dateutil.relativedelta.relativedelta(minutes=gap*i)
            time_start = start_date.strftime('%Y-%m-%dT%H:%M:%S')
            
            tweet_objects = self.getHistTweets(time_start)
            
            # add results to dictionary with key as its time_start value
            hist_tweet_object['time']= time_start
            hist_tweet_object['tweets'] = tweet_objects
            
            list_hist_tweet_objects.append(hist_tweet_object)
        return list_hist_tweet_objects
    
    # External function that returns historical tweets related to cryptocurrency markets
    # getHistTweets(time_start = string, time_end = string, limit = int)
    # end_time optional, defaulted to None, request will pull tweets at start in chronological order until limit reached 
    # limit optional, defaulted to 100, each multiple of 100 counts as a request with the coinAPI interface
    # times follow ISO 8601 time format (YYYY-MM-DDThh:mm:ss)
    def getHistTweets(self, time_start, time_end=None, limit=100):
        # create request string specific to coinAPI method and execute
        if time_end == None:
            url = self._url_stem+'/twitter/history?time_start='+time_start+'&limit='+str(limit)
        else:
            url = self._url_stem+'/twitter/history?time_start='+time_start+'&time_end='+time_end+'&limit='+str(limit)
        response_object = requests.get(url, headers=self.headers)
        
        self._responseCheck(response_object)
        self._updateRequestLimits(response_object)
        # returning only the tweet objects within REST API response object
        return json.loads(response_object.text)
    
    # External function that saves tweet text in a csv format
    # saveTweetsText(list_hist_tweet_objects = list of historical twitter objects, outfile_name = string, looped = bool)
    # looped optional, defaulted to true, determines if list_hist_tweet_object is a list of coinAPI requests from 
    # loopHistTweets function or single list of tweet objects from getHistTweets function
    def saveTweetsText(self, list_hist_tweet_objects, outfile_name, looped=True):
        outfile_path = 'data/coin_tweets/'+outfile_name
        
        with open(outfile_path, 'w') as outfile:
            if looped:
                for hist_tweet_object in range(len(list_hist_tweet_objects)):
                    for tweet in range(len(list_hist_tweet_objects[hist_tweet_object]['tweets'])):
                        text = self._translate(list_hist_tweet_objects[hist_tweet_object]['tweets'][tweet]).encode('utf-8')
                        outfile.write("".join(text.splitlines())+'\n')
            else:
                for tweet in range(len(list_hist_tweet_objects)):
                    text = self._translate(list_hist_tweet_objects[tweet]).encode('utf-8')
                    outfile.write("".join(text.splitlines()))
            
            outfile.close()
    
    # External function that saves tweet objects in a json format 
    # saveTweets(list_of_tweet_objects = dict of twitter objects, outfile_name = string)
    def saveTweets(self, list_of_tweet_objects, outfile_name):
        outfile_path = 'data/coin_tweets/'+outfile_name
        with open(outfile_path, 'w') as outfile:
            json.dump(list_of_tweet_objects, outfile)
            outfile.close()
    
    # External function that opens file in json format and saves as json object (reverse of saveTweets)
    # openSavedTweets(infile_path = string) <--data/coin_tweets/file_name if used saveTweets function
    def openSavedTweets(self, infile_path):
        with open(infile_path) as json_file:
            data = json.load(json_file)
            json_file.close()
        return data
        
    # Internal function that translate tweet into english using googletrans and language noted by twitter user
    # _translate(tweet_object = twitter object)
    def _translate(self, tweet_object):
        try:
            lang = tweet_object['user']['lang'][:2]
            if lang != 'en':
                text = self.translator.translate(tweet_object['text'], src=lang, dest='en').text
            else:
                text = tweet_object['text']
        # exception handling for when 2 letter language code not recognized or no text value in twitter object
        except:
            if 'text' in tweet_object.keys():
                print "unable to translate: ",tweet_object['text']
                text = tweet_object['text']
            else:
                print "no text in tweet object"
                text = ''
            pass
        return text
    
    # Internal function that checks to ensure http request received a successful response (200)
    # _responseCheck(response_object = coinAPI response object)
    def _responseCheck(self, response_object):
        try:
            if int(response_object.status_code) == 200:
                pass
            else:
                raise UnsuccessfulRequest(response_object.status_code)
        except UnsuccessfulRequest as e:
            print "Unsuccessful Request: Response Code {0}, {1}".format(e.status_code, e.status_response)
    
    # Internal function that updates the request limits for that particular API Key
    # _updateRequestLimits(response_object = coinAPI response object)
    def _updateRequestLimits(self, response_object):
        self.request_limits = {'X-RateLimit-Limit': response_object.headers['X-RateLimit-Limit'], 
                               'X-RateLimit-Remaining': response_object.headers['X-RateLimit-Remaining'], 
                               'X-RateLimit-Request-Cost' : response_object.headers['X-RateLimit-Request-Cost'], 
                               'X-RateLimit-Reset' : response_object.headers['X-RateLimit-Reset']}
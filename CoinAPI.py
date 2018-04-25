import dateutil
import json
import requests
from googletrans import Translator

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
                               'X-RateLimit-RequestCost' : 0, 'X-RateLimit-Reset' : None}
       
    # External function that loops through historical tweets function and returns list of tweets
    # loopHistTweets(time_start = string, loops = int, gap = int)
    # loops optional, defaulted to 24, number of iterations, default set to 100 tweets per hour for 24 hours
    # gap optional, defaulted to 60, minutes between time_start iterations
    # time_start follows ISO 8601 time format (YYYY-MM-DDThh:mm:ss)
    def loopHistTweets(self, time_start, loops=24, gap=60):
        list_of_tweet_objects = {}
        
        for i in range(loops):
            # convert string to datetime, add gap time, convert back to string
            start_date = dateutil.parser.parse(time_start)
            start_date += dateutil.relativedelta.relativedelta(minutes=gap*i)
            time_start = date.strftime('%Y-%m-%dT%H:%M:%S')
            
            tweet_objects = self.getHistTweets(time_start)
            # add results to dictionary with key as its time_start value
            list_of_tweet_objects[time_start] = tweet_objects
        return list_of_tweet_objects
    
    # External function that returns historical tweets related to cryptocurrency markets
    # getHistTweets(time_start = string, time_end = string, limit = int)
    # end_time optional, defaulted to None, request will pull tweets at start in chronological order until limit reached 
    # limit optional, defaulted to 100, each multiple of 100 counts as a request with the coinAPI interface
    # times follow ISO 8601 time format (YYYY-MM-DDThh:mm:ss)
    def getHistTweets(self, time_start, time_end=None, limit=100):
        # create request string specific to coinAPI method and execute
        if time_end == None:
            url = self._url_stem+'/twitter/history?time_start='+time_start+'&limit'+str(limit)
        else:
            url = self._url_stem+'/twitter/history?time_start='+time_start+'&time_end'+time_end+'&limit'+str(limit)
        tweet_objects = requests.get(url, headers=self.headers)
        
        self._responseCheck(tweet_objects)
        self._updateRequestLimits(tweet_objects)
        return tweet_objects
    
    # External function that saves tweet text in a csv format
    # saveTweetsText(list_of_tweet_objects = dict of twitter objects, outfile_name = string)
    def saveTweetsText(self, list_of_tweet_objects, outfile_name):
        outfile_path = 'data/coin_tweets/'+outfile_name
        with open(outfile_path, 'w') as outfile:
            for tweet in list_of_tweet_objects:
                text = self._translate(tweet)
                outfile.write("".join(text.splitlines()))
            outfile.close()
    
    # External function that saves tweet objects in a json format 
    # saveTweets(list_of_tweet_objects = dict of twitter objects, outfile_name = string)
    def saveTweets(self, list_of_tweet_objects, outfile_name):
        outfile_path = 'data/coin_tweets/'+outfile_name
        with open(outfile_path, 'w') as outfile:
            json.dump(list_of_tweet_objects, outfile)
            outfile.close()
    
    # External function that opens .txt file in json format and saves as json object (reverse of saveTweets)
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
            text = self.translator.translate(tweet_object['text'], src=lang, dest='en').text
        except:
            print "unable to translate: ",tweet_object['text']
            text = tweet_object['text']
            continue
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
                               'X-RateLimit-RequestCost' : response_object.headers['X-RateLimit-RequestCost'], 
                               'X-RateLimit-Reset' : response_object.headers['X-RateLimit-Reset']}
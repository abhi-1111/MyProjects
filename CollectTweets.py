# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 08:52:26 2017

@author: cglynn

rest_query_movieTitle()
Retrieves Query data.  Collect current movie list for zip code and process 
    for querying and save to queryFile.  Removes stop words and punctuation from movie titles.

rest_query_movieTitlesTweets()
Collect Tweets retrieved when searching on movie titles for a specific zip code.  
    Saves collected tweets in retrievedFile.  Tweets saved in list have the form
    [text, id, id_str, created_at]  

rest_query_randomSample()
Collect Random Sample of Tweets and save to randomSampleFile.  Tweets are stored
    as a list in the form [text, id, id_str, created_at]  
"""

# -*- coding: utf-8 -*-

import tweepy, sys, json, time, urllib2, sets, string, stop_words

#==============================================================================
# Setup tweepy API and Global variables
#==============================================================================
reload(sys)
sys.setdefaultencoding("utf-8")

consumer_key='Okf8rnmarIctPnfjwfqMj9Fpf' 
consumer_secret='HakszG0KyyjYJxA0TraalLXY6bxBTEQBst5ZgHBw5IyoZg4WAM' 
access_token_key='832742214849531905-MwZ6NMLvO0zNf0XYewBS1VwAgBxj8aC'
access_token_secret='omcKXM1kOJOIMDclejLqdY8xwCwdmwgGPjnTpCAc90OW6'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)
myApi = tweepy.API(auth)
numberOfResults = 3000
tweetList = []
queryFile = 'query.data'
retrievedFile = 'retrievedTweets.data'
randomSampleFile = 'randomSampleTweets.data'
###############################################################################

#==============================================================================
# Setup Gracenot API for current movie titles
#Allows up to 50 calls per day; 2 calls per second.
#==============================================================================
consumer_key = 'wxsswsn7m4zhy823g957jbp4'
baseUrl = "http://data.tmsapi.com/v1.1"
showtimesUrl = baseUrl + '/movies/showings?'
zipCode = "12222"
date = time.strftime("%Y-%m-%d")
parameters = 'startDate=' + date + '&zip=' + zipCode + '&api_key=' + consumer_key
movieUrl = showtimesUrl + parameters
###############################################################################

#Retrieve Tweets based on current movie titles         
def rest_query_movieTitlesTweets():
    numMovies = 1
    with open(queryFile) as file:
        movieWordsFile = file.readlines()
        movieWords = json.loads(movieWordsFile[0])
    if(len(movieWords) > 1):
        numMovies = len(movieWords)
    resultCount = numberOfResults / numMovies
    numRepititions = resultCount / 100    
    if(numRepititions < 1):
        numRepititions = 1
    for movieTitle in movieWords:
        addTweets(movieTitle, numRepititions)
    with open(retrievedFile, 'w') as file:
        file.write(json.dumps(tweetList))
            
#Add tweets to list
def addTweets(queryString, numRepititions):
    geo = "42.6525,-73.7572,9mi" # City of Albany
    MAX_ID = None
    global tweetList
    tweets = myApi.search(q=queryString, geocode=geo, count=100, max_id = MAX_ID)
    tweets = myApi.search(q=queryString,  count=100, max_id = MAX_ID)
    for it in range(numRepititions):
        tweets = myApi.search(q=queryString, geocode=geo, count=100, max_id = MAX_ID)
        tweets = myApi.search(q=queryString, count=100, max_id = MAX_ID)
        if tweets:
            MAX_ID = tweets[-1].id
            for tweet in tweets:
                tweetList.append(convertTweepyObjToDict(tweet))
    

#Retrieve movie Titles
def rest_query_movieTitle():
    request = urllib2.Request(movieUrl)
    movieSet = sets.Set()
    movieDictionary = dict()
    global queryList
    rootIds = []  # used to not duplicate movie titles.
    try:
        response = urllib2.urlopen(request)
        movies = response.read()
        movieDictionary = json.loads(movies)
    except urllib2.URLError, e:
        print 'Error connecting to Movie API: ' , e
    for movie in movieDictionary:
        if movie['rootId'] not in rootIds:
            rootIds.append(movie['rootId'])
            title = removeStopWords(removePunctuation(movie['title'].lower()))
            title.append('movie')
            if len(title) > 1: #Ensure more than one word in title.
                movieSet.add(' '.join([str(x) for x in title]))
    movieList = list(movieSet)
    with open(queryFile, 'w') as file:
        file.write(json.dumps(movieList))  
    

#Remove punctuation
def removePunctuation(text):
#    Replace 's and n't    
    text = text.replace("'s",'')
    text = text.replace("n't", '')
    for p in string.punctuation:
        text = text.replace(p,'')
    return text

#Remove Stopwords
def removeStopWords(textInput):
    import datetime
    tempText = textInput.split()
    now = datetime.datetime.now()
    stopWords = stop_words.get_stop_words('english')
    addStopWordsList = [str(now.year), '3d', '2', 'get', 'movie']
    addStopWords(stopWords, addStopWordsList)
    wordsList = textInput.split()
    for word in wordsList:
        try:
            stopWords.index(word)
            tempText.remove(word)
        except Exception:
            pass
    clean_stopWords(stopWords, addStopWordsList)
    return tempText
    

#Retrieve Random Sample
def rest_query_randomSample():
    numResults = 3000
    geo = "42.6525,-73.7572,9mi" # City of Albany
    MAX_ID = None
    tweetList = []
    tweets = myApi.search(geocode=geo,count=numResults, max_id = MAX_ID)
    tweets = myApi.search(q="a",count=numResults, max_id = MAX_ID)
    for it in range(20): 
        tweets = myApi.search(geocode=geo,count=numResults, max_id = MAX_ID)
        tweets = myApi.search(q="a",count=numResults, max_id = MAX_ID)
        if tweets:
            MAX_ID = tweets[-1].id
            for tweet in tweets:
                tweetList.append(convertTweepyObjToDict(tweet))
    with open(randomSampleFile, 'w') as file:
        file.write(json.dumps(tweetList))       

def convertTweepyObjToDict(tweepyObject):
    return {
         'text': tweepyObject.text,
         'id': tweepyObject.id,
         'id_str': tweepyObject.id_str,
         'created_at': str(tweepyObject.created_at), 
    }
    
def clean_stopWords(stopWords, removeStopWordsList):
    for word in removeStopWordsList:
        stopWords.remove(word)

def addStopWords(stopWords, addStopWordsList):
    for word in addStopWordsList:
        stopWords.append(word)

if __name__ == '__main__':
    rest_query_randomSample()
    rest_query_movieTitle()
    rest_query_movieTitlesTweets()
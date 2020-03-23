"""
@author: BURHAN AWAN (2490836A)
"""
import csv
import emoji
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import enchant as eht
import numpy as np
import string
import tokenize
import pytypo
import gensim
import pandas as pd
from textblob import TextBlob, Word
from spellchecker import SpellChecker
from pycontractions import Contractions
from gingerit.gingerit import GingerIt

#Some Class Definitons:
class listener(StreamListener):
    
    #def on_status(self, status):
        #print(status.text)
        
    def on_error(self, status):
        if status == 420: #to prevent lack of access to tweets
            return False

#Some Function Definitions:
#Code Will remove retweets as they contain duplicate content
def appender(lst, query, num, Api):#will append "num" tweets based on "query" to list "lst" using API "Api. It will also remove retweets. These tweets will usually contain hashtags" 
    sample_tweets = tweepy.Cursor(Api.search, q = ( "# " + query + " -filter:retweets"), lang = "en", tweet_mode = 'extended').items(num)
    for tweet in sample_tweets:
        lst.append(tweet)

#Code does not process links/URLs in tweets properly.
#Code will remove newline characters in tweets during processing (done as part of Task #2)
#Code will not process non-english names correctly (it would be useful to add them to relevant lexicons)
#Code does not process the '£' sign properly
cont = Contractions(api_key="glove-twitter-25")#this will be used in tweet_Processor to expand contractions        
#cont.load_models()

d =eht.Dict("en_GB")#this will be used in tweet_Processor to detect words outside the British English Dictionary
sc = SpellChecker()
parser = GingerIt()#for grammar correction

#Task 2 related stuff covered here. It was decided that using .json files is not efficient
def tweet_Processor(tweet): 
    sentences = sent_tokenize(str(tweet.full_text))
    for s in range(len(sentences)):
        sentences[s] = pytypo.correct_sentence(sentences[s])#eliminating word lenghtening errors
        sentences[s] = list(cont.expand_texts([sentences[s]]))[0]#expanding contractions
        words_in_sentence = word_tokenize(sentences[s])

        for w in range(len(words_in_sentence)):# loop through words in sentence[s]
            if (words_in_sentence[w] in string.punctuation):# if word is punctuation mark do nothing to it
                pass
            else:
                if (not (d.check(words_in_sentence[w]))):#if word not in dictionary
                    words_in_sentence[w] = sc.correction(words_in_sentence[w])#attempt to bring it in dictionary
                    if (not (d.check(words_in_sentence[w]))):#if still outside dictionary
                        if (len(d.suggest(words_in_sentence[w])) > 0):
                            words_in_sentence[w] = d.suggest(words_in_sentence[w])[0]
                        else:
                            pass
                    else:
                        pass
                else:#numbers will not be changed#
                    pass
        sentences[s] = TreebankWordDetokenizer().detokenize(words_in_sentence)#once words in sentence have been modified reform sentence
        sentences[s] = list(cont.expand_texts([sentences[s]]))[0]#for expanding remaining contractions
        sentences[s] = parser.parse(sentences[s])['result']#for eliminating grammatical errors        
    tweet.full_text = TreebankWordDetokenizer().detokenize(sentences)     
    
#Main Program is as follows:
if __name__  == "__main__":
    #Authentication of Application
    consumer_key = "5MmA8BtLad7O8wxo9XhxWG3ig"
    consumer_secret = "r3LNMMuoOHapLDQhOjRR80lWMwSGIHhxG610DVnhgjzGq2ExaQ"
    access_token = "1225416534576828417-uuh3oH0Za14oURsYTd0IsUDdlBbWdT"
    access_token_secret = "plXZCiPZ69W41D9p9Zwdy2g04IjkcZ5P6yYfdCzxqkgwG"
    
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
            
    #Text to be used during Filtration later in the Code
    fl_pleasant = ['positive', 'pleasant', 'good', 'nice']
    fl_excitement = ['excited', 'excitement', 'exciting', 'energizing', 'galvinizing'] 
    fl_happy = ['happpy', 'joy', 'love', 'happiness', 'loving']
    fl_surprise = ['negative', 'sad', 'frustration', 'sadness', 'surprise', 'frustrated']
    fl_angry = ['anger', 'rage', 'outrage', 'angry', 'enraged']
    fl_fear = ['fear', 'disgust', 'depression', 'depressed', 'disgusted']
    fl = fl_pleasant + fl_excitement + fl_happy + fl_surprise + fl_angry + fl_fear
    
    #Hashtag strings that will be used later
    ht_pleasant = "positive, pleasant, good, nice, POSITIVE"
    ht_excitement = "excited, excitement, exciting, energizing, galvinizing"  
    ht_happy = "happpy, joy, love, happiness, loving"
    ht_surprise = "negative, sad, frustration, sadness, surprise, frustrated"
    ht_angry = "anger, rage, outrage, angry, enraged"
    ht_fear = "fear, disgust, depression, depressed, disgusted"
    
    #Variables for storing "Tweet Count" of each of the 6 Emotion Classes:
    nt_p, nt_e, nt_h, nt_s, nt_a, nt_f = 0, 0, 0, 0, 0, 0
    
    #Preparing the .csv files (one such file per emotion class)
    
    fieldnames = ['Tweet ID', 'Text of Tweet', 'Created at Info.']
    with open('pleasant.csv', mode='w') as csv_file:
        writer_pleasant = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer_pleasant.writeheader()
        
    with open('excitement.csv', mode='w') as csv_file:
        writer_excitement = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer_excitement.writeheader()

    with open('happy.csv', mode='w') as csv_file:
        writer_happy = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer_happy.writeheader()

    with open('surprise.csv', mode='w') as csv_file:
        writer_surprise = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer_surprise.writeheader()

    with open('angry.csv', mode='w') as csv_file:
        writer_angry = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer_angry.writeheader()

    with open('fear.csv', mode='w') as csv_file:
        writer_fear = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer_fear.writeheader()

    

    #stream.filter(track = fl)#it was later determined that this only filters out tweets during live streaming and therefore is useless in my current code
    #While Loop #1:
    while (nt_p < 150):
        #Generating list of tweets
        tweets = []
        for entry in fl_pleasant:
            appender(tweets, entry, 30, api)
            
       #Classifying tweets based on emotion classes. #Task 2 related stuff covered here. Use of.json files was abondoned due to lack of need    
        for i in range(len(tweets)):
            sent_count = len(sent_tokenize(tweets[i].full_text))#Number of sentences in tweet text
            ht_count = len(tweets[i].entities.get('hashtags'))#Number of hashtags in tweet text
            em_count = emoji.emoji_count(tweets[i].full_text)
            if ((0 < sent_count < 5) and (ht_count == 1) and (em_count == 0)):#lots of tweets have one hashtag 
                ht_text = str(tweets[i].entities.get('hashtags')[0]['text'])
                if (ht_text in ht_pleasant):
                    nt_p += 1
                    tweet_Processor(tweets[i])#Processing tweet
                    #Storing tweet
                    with open('pleasant.csv', mode='a') as csv_file:
                        writer_pleasant = csv.DictWriter(csv_file, fieldnames=fieldnames)
                        writer_pleasant.writerow({'Tweet ID': tweets[i].id_str, 'Text of Tweet': tweets[i].full_text, 'Created at Info.': tweets[i].created_at})
                        

    #While Loop #2:
    while (nt_e < 150):
        #Generating list of tweets
        tweets = []
        for entry in fl_excitement:
            appender(tweets, entry, 30, api)

        #Classifying tweets based on emotion classes. #Task 2 related stuff covered here. Use of.json files was abondoned due to lack of need    
        for i in range(len(tweets)):
            sent_count = len(sent_tokenize(tweets[i].full_text))#Number of sentences in tweet text
            ht_count = len(tweets[i].entities.get('hashtags'))#Number of hashtags in tweet text
            em_count = emoji.emoji_count(tweets[i].full_text)
            if ((0 < sent_count < 5) and (ht_count == 1) and (em_count == 0)):#lots of tweets have one hashtag 
                ht_text = str(tweets[i].entities.get('hashtags')[0]['text'])
                if (ht_text in ht_excitement):
                    nt_e += 1
                    tweet_Processor(tweets[i])#Processing tweet
                    #Storing tweet
                    with open('excitement.csv', mode='a') as csv_file:
                        writer_excitement = csv.DictWriter(csv_file, fieldnames=fieldnames)
                        writer_excitement.writerow({'Tweet ID': tweets[i].id_str, 'Text of Tweet': tweets[i].full_text, 'Created at Info.': tweets[i].created_at})
   

    #While Loop #3:
    while (nt_h < 150):
        #Generating list of tweets
        tweets = []
        for entry in fl_happy:
            appender(tweets, entry, 30, api)

        #Classifying tweets based on emotion classes. #Task 2 related stuff covered here. Use of.json files was abondoned due to lack of need    
        for i in range(len(tweets)):
            sent_count = len(sent_tokenize(tweets[i].full_text))#Number of sentences in tweet text
            ht_count = len(tweets[i].entities.get('hashtags'))#Number of hashtags in tweet text
            em_count = emoji.emoji_count(tweets[i].full_text)
            if ((0 < sent_count < 5) and (ht_count == 1) and (em_count == 0)):#lots of tweets have one hashtag 
                ht_text = str(tweets[i].entities.get('hashtags')[0]['text'])
                if (ht_text in ht_happy):
                    nt_h += 1
                    tweet_Processor(tweets[i])#Processing tweet
                    #Storing tweet
                    with open('happy.csv', mode='a') as csv_file:
                        writer_happy = csv.DictWriter(csv_file, fieldnames=fieldnames)
                        writer_happy.writerow({'Tweet ID': tweets[i].id_str, 'Text of Tweet': tweets[i].full_text, 'Created at Info.': tweets[i].created_at})

    #While Loop #4:
    while (nt_s < 150):
        #Generating list of tweets
        tweets = []
        for entry in fl_surprise:
            appender(tweets, entry, 30, api)

        #Classifying tweets based on emotion classes. #Task 2 related stuff covered here. Use of.json files was abondoned due to lack of need    
        for i in range(len(tweets)):
            sent_count = len(sent_tokenize(tweets[i].full_text))#Number of sentences in tweet text
            ht_count = len(tweets[i].entities.get('hashtags'))#Number of hashtags in tweet text
            em_count = emoji.emoji_count(tweets[i].full_text)
            if ((0 < sent_count < 5) and (ht_count == 1) and (em_count == 0)):#lots of tweets have one hashtag 
                ht_text = str(tweets[i].entities.get('hashtags')[0]['text'])
                if (ht_text in ht_surprise):
                    nt_s += 1
                    tweet_Processor(tweets[i])#Processing tweet
                    #Storing tweet
                    with open('surprise.csv', mode='a') as csv_file:
                        writer_surprise = csv.DictWriter(csv_file, fieldnames=fieldnames)
                        writer_surprise.writerow({'Tweet ID': tweets[i].id_str, 'Text of Tweet': tweets[i].full_text, 'Created at Info.': tweets[i].created_at})

    
    #While Loop #5:
    while (nt_a < 150):
        #Generating list of tweets
        tweets = []
        for entry in fl_angry:
            appender(tweets, entry, 30, api)

        #Classifying tweets based on emotion classes. #Task 2 related stuff covered here. Use of.json files was abondoned due to lack of need    
        for i in range(len(tweets)):
            sent_count = len(sent_tokenize(tweets[i].full_text))#Number of sentences in tweet text
            ht_count = len(tweets[i].entities.get('hashtags'))#Number of hashtags in tweet text
            em_count = emoji.emoji_count(tweets[i].full_text)
            if ((0 < sent_count < 5) and (ht_count == 1) and (em_count == 0)):#lots of tweets have one hashtag 
                ht_text = str(tweets[i].entities.get('hashtags')[0]['text'])
                if (ht_text in ht_angry):
                    nt_a += 1
                    tweet_Processor(tweets[i])#Processing tweet
                    #Storing tweet
                    with open('angry.csv', mode='a') as csv_file:
                        writer_angry = csv.DictWriter(csv_file, fieldnames=fieldnames)
                        writer_angry.writerow({'Tweet ID': tweets[i].id_str, 'Text of Tweet': tweets[i].full_text, 'Created at Info.': tweets[i].created_at})

                    
    #While Loop #6:
    while (nt_f < 150):
        #Generating list of tweets
        tweets = []
        for entry in fl_fear:
            appender(tweets, entry, 30, api)

        #Classifying tweets based on emotion classes. #Task 2 related stuff covered here. Use of.json files was abondoned due to lack of need    
        for i in range(len(tweets)):
            sent_count = len(sent_tokenize(tweets[i].full_text))#Number of sentences in tweet text
            ht_count = len(tweets[i].entities.get('hashtags'))#Number of hashtags in tweet text
            em_count = emoji.emoji_count(tweets[i].full_text)
            if ((0 < sent_count < 5) and (ht_count == 1) and (em_count == 0)):#lots of tweets have one hashtag 
                ht_text = str(tweets[i].entities.get('hashtags')[0]['text'])
                if (ht_text in ht_fear):
                    nt_f += 1
                    tweet_Processor(tweets[i])#Processing tweet
                    #Storing tweet
                    with open('fear.csv', mode='a') as csv_file:
                        writer_fear = csv.DictWriter(csv_file, fieldnames=fieldnames)
                        writer_fear.writerow({'Tweet ID': tweets[i].id_str, 'Text of Tweet': tweets[i].full_text, 'Created at Info.': tweets[i].created_at})


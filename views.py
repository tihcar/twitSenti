# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 20:45:47 2017

@author: Rachit & Nitesh
"""

from flask import render_template,url_for, flash, redirect, request
from pycountry import countries
from flask import Markup
from main import app
from sentimentCalculator import tweetsSenti
import os

# from markupsafe import Markup
# index view function suppressed for brevity

#@app.route('/')
#def yo():
#	#creating a variable for create page, method name for 'create' should be same
#	createLink = '<a href=' + url_for('hello') + '>Click here to enter the website</a>'
#	return '<html><head>Home Page</head><body>'+ createLink +'</body></html>'


@app.route('/', methods=['GET','POST'])
def hello():
    if request.method=='GET':
        path=os.getcwd()
        fullPath=os.path.join(path,'Databases\\LikeCount.txt')
        countFileR=open(fullPath,'r')
        count = countFileR.read()
        countFileR.close()

        return render_template('hello.html',likesCount = count, buttonVisibility = 'visible')
    elif request.method=='POST':
        twitterHandle = request.form['twitterhandle']
        buttonVisibility = request.form['likeButtonVisibilityValue']
        tweetCountDropDown = request.form['tweetCountDropDown']

        #Fetching current likes from database
        path=os.getcwd()
        fullPath=os.path.join(path,'Databases\\LikeCount.txt')
        countFileR=open(fullPath,'r')
        count = countFileR.read()
        countFileR.close()

        obj=tweetsSenti()
        world_map_string, world_map_ids, us_map_string, us_map_ids, world_tweets_count, world_country_df,country_tweets_count, summary_df_Country, bar_string, bar_ids = obj.searchTweets(twitterHandle,tweetCountDropDown)
        if(world_map_string==""):
            return render_template('hello.html', worldPlot = world_map_string, world_map_ids = world_map_ids, usaMapPlot = us_map_string, usa_map_ids = us_map_ids, 
                              world_tweets_count = world_tweets_count, world_country_df = world_country_df,country_tweets_count=country_tweets_count, summary_df_Country = summary_df_Country,
                              bar_string = bar_string, bar_ids = bar_ids, exception = "Raise Exception", likesCount = count,buttonVisibility = buttonVisibility)
        else:
            return render_template('hello.html', worldPlot = world_map_string, world_map_ids = world_map_ids,
                                  usaMapPlot = us_map_string, usa_map_ids = us_map_ids, world_tweets_count = world_tweets_count, world_country_df = world_country_df,
                                  country_tweets_count=country_tweets_count, summary_df_Country = summary_df_Country,
                                  barPlot = bar_string, bar_ids = bar_ids, likesCount = count,buttonVisibility = buttonVisibility)
       

@app.route('/likeButtonAction', methods=['POST'] )
def likeButton():
     value = request.form['hiddenButtonValue']
     
     fullPath=''
     newCount = 0
     if value =="like":
        path=os.getcwd()
        fullPath=os.path.join(path,'Databases\\LikeCount.txt')
        likeFileR=open(fullPath,'r')
        oldLikeCount = likeFileR.read()
        likeFileR.close()
        newCount= int(oldLikeCount) + 1
     elif value=="dislike":
        path=os.getcwd()
        fullPath=os.path.join(path,'Databases\\DislikeCount.txt')
        dislikeFileR=open(fullPath,'r')
        oldDislikeCount = dislikeFileR.read()
        dislikeFileR.close()
        newCount= int(oldDislikeCount) + 1
     
     if fullPath!='':
         fileW = open(fullPath,'w')
         if newCount != 0:
             fileW.write(str(newCount))
         fileW.close() 
        
     return "",204   

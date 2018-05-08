# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 20:45:47 2017

@author: Rachit & Nitesh
"""
import json

class tweetsSenti:

    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

    def searchTweets(self, q, ct):
        import numpy as np
        import pandas as pd
        import re
        from twitter import Twitter, OAuth, TwitterHTTPError
        from pandas.io.json import json_normalize
        from pycountry import countries
        
        ACCESS_TOKEN = '136600388-9iihe7SFq8nZUOL5GjxoZlPbxW2MYcScWlZ6sD3a'
        ACCESS_SECRET = 'ScmAR4iYHCxuPHhYMifirTK0h2Jhdqt1p10uoz9lHTshT'
        consumer_key = 'bto0MsRvjjfkrl4QpndjaUneg'
        consumer_secret = '5zr7Xr9y4AbKgUCuWRmQGaMvizwg48HpVeyjbSZC4j350rIYPF'
        
        oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, consumer_key, consumer_secret)
        twitterObj = Twitter(auth=oauth)
        
        count = int(ct)
       
        try:
            search_results = twitterObj.search.tweets(q=q,count = count)
        except TwitterHTTPError:
            return "","","","","","","","","",""
        
        if(search_results['statuses']==[]):
            return "","","","","","","","","",""

        Original_status_df = json_normalize(search_results,['statuses'])
        Original_status_df = pd.DataFrame(Original_status_df)
        min_id = min(Original_status_df['id'])
        max_id = max(Original_status_df['id'])

        while len(Original_status_df) < count:
            try:
                search_results = twitterObj.search.tweets(q=q,count=count,max_id = min_id)
                results = json_normalize(search_results,['statuses'])
                Original_status_df = Original_status_df.append(results)
                min_id = min(results['id'])
                max_id = max(results['id'])
            except TwitterHTTPError:
                return "","","","","","","","","",""

        countries_name=[]
        Original_status_df = Original_status_df.reset_index()
        cleansed_tweets_df = clean_Tweets(Original_status_df)
        for c in list(countries):
            countries_name.append(c.name)
        
        #countries_name = ['Argentina','Austria','Australia','Brasil','Brazil','Bangladesh','Cameroon','Canada','Cyprus',
        #            'Deutschland','Dubai','Ecuador','Egypt',
        #            'England','Kenya','Nigeria','Hong Kong','Holand','Finland','Prague','USA','Greece',
        #            'Kazakhstan','Thailand','Italy','Italia','India','Israel','Ireland','Pakistan','Polska','Poland',
        #            'United States','Germany','Spain','France','Fiji','China','Mexico','Netherlands',
        #            'New Zealand','North Korea','Japan','Jordan',
        #            'Oman','Palestine','United Arab Emirates','UAE','Portugal','Scotland','Slovakia',
        #            'South Africa','Switzerland','Sweden',
        #            'Turkey','Peru','Puerto Rico','Russia','Singapore','Chile','United Kingdom','Indonesia','Philippines',
        #            'Ukraine','UK','Venezuela','Yemen']

        Cleansed_Country_df = Country_of_tweet(cleansed_tweets_df,countries_name)

        us_city_state_filter =['Albuquerque','Asheville','Atlanta','Austin','Baltimore','Boston','Columbia','Dallas','Detroit','Denver',
                       'Las Vegas','Georgia','Miami','Honolulu','Los Angeles','Pensacola','Richmond','Kansas',
                       'Pheonix City','Washington, DC','NYC',
                       'San Jose','Seattle','Orlando','Pittsburgh','San Diego','Chicago',    
                       'New York','Phoenix','Mount Prospect',
                       'Alabama','Alaska','Arkansas','Arizona',
                       'California','Colorado','Connecticut','Delaware','Florida','Hawaii','Indiana','Iowa','Idaho','Illinois',
                       'Indiana','Louisiana','Oregon',       
                       'Maryland','Michigan','Minnesota','Maine','Massachusetts','Missouri','Mississippi','Montana',
                       'Nebraska','New Jersey','New Hampshire','North Carolina','Kentucky','Ohio','Oklahoma',
                       'New Mexico','Nevada','North Dakota','South Dakota','Pennsylvania','San Francisco',
                       'Tennessee','Utah','Rhode Island','South Carolina','Washington','West Virginia','Wisconsin','Wyoming',
                       'Texas','Vermont','Virginia','LA','SF',
                       'AZ','AL','CA','CO','CT','DE','FL','GA','IA','ID','IL','IN','KY','MA',
                       'MI','MO','MD','MT','MN','MS','NC','ND','NJ','NH','NY','NV',
                       'OH','OR','PA','RI','SD','TX','TN','UT','VA','VT','WA','WI','WY','WV']
        
        US_States_df = US_State_of_User(Cleansed_Country_df,us_city_state_filter)
        updated_country_df = Updated_country_of_tweet(US_States_df,'USA')
        only_country_df =   updated_country_df[updated_country_df['Country_User']!=''].reset_index(drop=True)
      
        tweet_df_live_sentiments_df = calculate_sentiment(only_country_df)

        country_tweets_count  = countryTweetsCount(tweet_df_live_sentiments_df)
        usa_tweets_count    = usaTweetsCount(country_tweets_count)

        converted_country_df = ConvertCountryName(usa_tweets_count)
      
        mean_sentiments_country_df = meanSentimentsCountry(converted_country_df)
        mean_sentiments_UsState_df = meanSentimentsUsState(mean_sentiments_country_df)

        summary_df_world = dataSummaryWorld(mean_sentiments_UsState_df)
        summary_df_Country = dataSummaryCountry(mean_sentiments_UsState_df,'USA')

        world_map_df  = mean_sentiments_UsState_df[['Country_User_Code','Mean_Polarity_Country','Weighted_Mean_Polarity_Country','Total_Tweets_Country']]
        world_map =  world_map_df.groupby('Country_User_Code').mean()
        
        UsState_map_df  = mean_sentiments_UsState_df[['USA_State_User_Code','Mean_Polarity_USA_State','Weighted_Mean_Polarity_USA_State','Total_Tweets_USA_State']]
        UsState_map =  UsState_map_df.groupby('USA_State_User_Code').mean()

        bar_df = mean_sentiments_UsState_df[['Weighted_Mean_Polarity_Country','Weighted_Mean_Subjectivity_Country','created_at']]
        times =pd.to_datetime(bar_df['created_at'])
        bar_df.index = times
        bar_df = bar_df.resample('T').mean()

        bar_string, bar_ids = bar_sentiments(bar_df['Weighted_Mean_Polarity_Country'],bar_df['Weighted_Mean_Subjectivity_Country'],bar_df.index)
        
        world_map_string, world_map_ids = worldMap(world_map['Weighted_Mean_Polarity_Country'], world_map.index)
        us_map_string, us_map_ids = UsMapPlot(UsState_map['Weighted_Mean_Polarity_USA_State'],UsState_map.index)
       
        return world_map_string, world_map_ids, us_map_string, us_map_ids, summary_df_world['# Tweets'].sum(), summary_df_world.to_html(justify='justify'),summary_df_Country['# Tweets'].sum(),summary_df_Country.to_html(justify='justify'), bar_string, bar_ids


def clean_Tweets(Original_status_df):
    import re
    status_row = []
    location=[]
    tweet_df = Original_status_df[['user','text','created_at']]
    for i in range(len(tweet_df)):
        status_ = tweet_df.iloc[i,:]['text'].lower()
        status_ = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',status_)
        status_ = re.sub('@[^\s]+','',status_)
        status_ = re.sub('[^A-Za-z0-9 ]+', '', status_)
        status_ = status_.replace('rt','')
        status_row.append(status_)
        
        try:
            location_ = tweet_df.iloc[i,:]['user']['location']
            location.append(location_)
        except IndexError:
            location.append("")

    tweet_df['text'] = status_row
    tweet_df['Location_User'] = location
   
    return tweet_df


def Country_of_tweet(dataframe,countries_filter):
    import re
    list3 =[]
    country_names_updated = {'Prague' : 'Czechia','United States':'USA','United Arab Emirates':'UAE',
                             'Deutschland':'Germany','UK':'United Kingdom','Italia':'Italy','Polska':'Poland',
                             'Holand':'Netherlands','Brasil':'Brazil'}
    for i in range(len(dataframe)):
        setblank =0
        location = dataframe.iloc[i,:]['Location_User']
        if(isinstance(location,str)):
            location_split = re.split(r'[-,.\s]',location)
            for country in countries_filter:
                if('United Arab Emirates' in country or 'United States' in country or 'United Kingdom' in country 
                   or 'New Zealand' in country or 'North Korea' in country):
                    if(re.search(country,location) or re.search(country.lower(),location.lower()) or re.search(country.upper(),location.upper())):
                        country_updated = country_names_updated.get(country,country)
                        list3.append(country_updated) 
                        setblank = 1
                        break 
                elif(country in location_split or country.lower() in location_split or country.upper() in location_split):
                    country_updated = country_names_updated.get(country,country)
                    list3.append(country_updated)
                    setblank = 1
                    break
               
            if(setblank == 0):
                list3.append('')
        else:
            list3.append('')
        
    dataframe['Country_User'] = list3
    return dataframe


def US_State_of_User(dataframe,us_city_state):
    import re
    import us

    dummylist =[]
    count = 0
    city_to_state_names_updated = {'Albuquerque':'New Mexico',
                                   'Atlanta':'Georgia',
                                   'Austin':'Texas',
                                   'Baltimore':'Maryland',
                                   'Boston':'Massachusetts',
                                   'Columbia':'South Carolina',
                                   'Diego':'California',
                                   'Denver':'Colorado',
                                   'Detroit':'Michigan',
                                   'Honolulu':'Hawaii',
                                   'Las Vegas' : 'Nevada',
                                   'Vegas':'Nevada',
                                   'Indianapolis':'Indiana',
                                   'Dallas': 'Texas',
                                   'Seattle': 'Washington',
                                   'NYC':'New York',
                                   'Los Angeles' : 'California',
                                   'Orlando': 'Florida',
                                   'San Diego' : 'California',
                                   'San Jose':'California',
                                   'San Francisco':'California',
                                   'LA':'California',
                                   'SF':'California',
                                   'Pittsburgh':'Pennsylvania',
                                   'Pensacola':'Florida',
                                   'Chicago':'Illinois','Phoenix':'Arizona','Pheonix City':'Albama','Richmond':'Virginia',
                                   'Mount Prospect':'Illinois','Washington  DC':'Maryland','washington, DC':'Maryland',                             
                                   'Miami':'Florida', 'Asheville':'North Carolina','Washington DC':'Maryland',
                                   'AZ':'Arizona','AL':'Alabama','CA':'California','CT':'Connecticut','CO':'Colorado',
                                   'DE':'Delaware','FL':'Florida','GA':'Georgia','ID':'Idaho','IA':'Iowa','IL':'Illinois',
                                   'IN':'Indiana','KY':'Kentucky','MA':'Massachusetts','MD':'Maryland','MI':'Michigan',
                                   'MN':'Minnesota','MS':'Mississippi','MT':'Montana','MO':'Missouri','NC':'North Carolina',
                                   'ND':'North Dakota','NE':'Nebraska','NH':'New Hampshire','NY':'New York',
                                   'NJ':'New Jersey','NV':'Nevada','OH':'Ohio','OR':'Oregon','PA':'Pennsylvania',
                                   'RI':'Rhode Island','TX':'Texas','TN':'Tennessee','SD':'South Dakota','UT':'Utah',
                                   'VA':'Virginia','VT':'Vermont','WA':'Washington','WI':'Wisconsin','WY':'Wyoming',
                                   'WV':'West Virginia'}
    
    for i in range(len(dataframe)):
        setblank =0
        location_string =  dataframe.iloc[i,:]['Location_User']
        if(isinstance(location_string,str)):
            location_string_split= re.split(r'[,\s]', location_string)
            for city_state in us_city_state:
                if('New York' in city_state or 'Las Vegas' in city_state or 'Los Angeles' in city_state 
                   or 'North Carolina' in city_state or 'San Francisco' in city_state or 'New Mexico' in city_state 
                   or 'North Dakota' in city_state or 'South Dakota' in city_state or 'Rhode Island' in city_state 
                   or 'Washington, DC' in city_state or 'New Jersey' in city_state or 'Washington DC' in city_state
                   or 'Washington  DC' in city_state or 'New Hampshire' in city_state or 'West Virginia' in city_state):
                    if(re.search(city_state,location_string) or re.search(city_state.lower(),location_string.lower()) 
                       or re.search(city_state.upper(),location_string.upper())):
                        state_updated = city_to_state_names_updated.get(city_state,city_state)
                        dummylist.append(state_updated) 
                        setblank = 1
                        break
                elif(city_state in location_string_split or city_state.upper() in location_string_split):
                    state_updated = city_to_state_names_updated.get(city_state,city_state)
                    dummylist.append(state_updated) 
                    setblank = 1
                    break
                elif(city_state.lower() in location_string_split):
                    if(len(city_state)!=2):
                       state_updated = city_to_state_names_updated.get(city_state,city_state)
                       dummylist.append(state_updated)
                       setblank = 1
                       break    
            if(setblank == 0):
                dummylist.append('')
        else:
            dummylist.append('')

    final_list = []
    dataframe['USA_State_User'] = dummylist
    map_states_codes = us.states.mapping('name','abbr')
    for i in range(len(dummylist)):
        final_list.append(map_states_codes.get(dummylist[i]))

    for i in range(len(final_list)):
        if (final_list[i]==None):
            final_list[i]=''

    dataframe['USA_State_User_Code'] = final_list
    
    return dataframe

def Updated_country_of_tweet(dataframe,country):
       
    countrylist = []
    for i in range(len(dataframe)):
        if(dataframe.iloc[i,:]['USA_State_User']!=''):
            countrylist.append(country)
        else:
            countrylist.append(dataframe.iloc[i,:]['Country_User'])
            
    dataframe['Country_User'] = countrylist
    return  dataframe 

def ConvertCountryName(dataframe):
    import pycountry as pyc
    world_dict = dict()
    world_dict['']=''
    world_dict['USA'] = 'USA'
    world_dict['Dubai'] = 'UAE'
    world_dict['Russia'] = 'RUS'
    for countryValue in pyc.countries:
        country_code = countryValue.alpha_3
        country_name = countryValue.name
        world_dict[country_name] = country_code
    countryCodes =[]
    for i in range(len(dataframe)):
        try:
            country = dataframe.iloc[i,:]['Country_User']
            countryCodes.append(world_dict[country])
        except KeyError:
            countryCodes.append('')
    
    dataframe['Country_User_Code'] = countryCodes
    return dataframe



def calculate_sentiment(tweet_df):
    from textblob import TextBlob
    polarity = []
    subjectivity = []
    reputation = []
    for i in range(len(tweet_df)):
        wiki = TextBlob(tweet_df.iloc[i,:]['text'])
        polarity.append(wiki.sentiment.polarity)
        subjectivity.append(wiki.sentiment.subjectivity)
        try:
            reputation.append(int(tweet_df.iloc[i,:]['user']['followers_count'])/(int(tweet_df.iloc[i,:]['user']['followers_count'])
            + int(tweet_df.iloc[i,:]['user']['friends_count'])))
        except ValueError:
            reputation.append(0)
        except ZeroDivisionError:
            reputation.append(0)
    tweet_df['Polarity'] = polarity
    tweet_df['Subjectivity']= subjectivity
    tweet_df['Reputation'] = reputation
    tweet_df['Reputation'] = round(tweet_df['Reputation'],1)
    return tweet_df

def countryTweetsCount(dataframe):
    import numpy as np
    dataframe['Total_Tweets_Country']=int()
    for country in dataframe.Country_User.unique():
        if(country == ''):
            dataframe.loc[dataframe.Country_User==country,'Total_Tweets_Country']= np.nan
        else:
            dataframe.loc[dataframe.Country_User==country,'Total_Tweets_Country'] = (dataframe[dataframe.Country_User==country].count().values[3])

    return dataframe

def usaTweetsCount(dataframe):
    import numpy as np
    dataframe['Total_Tweets_USA_State']=int()
    for state in dataframe.USA_State_User.unique():
        if(state == ''):
            dataframe.loc[dataframe.USA_State_User==state,'Total_Tweets_USA_State']= np.nan
        else:
            dataframe.loc[dataframe.USA_State_User==state,'Total_Tweets_USA_State'] = (dataframe[dataframe.USA_State_User==state].count().values[4])

    return dataframe

def meanSentimentsCountry(dataframe):
    dataframe['Mean_Polarity_Country']=float()
    dataframe['Mean_Subjectivity_Country']=float()
    dataframe['Mean_Reputation_Country']=float()
    dataframe['Weighted_Mean_Polarity_Country']=float()
    dataframe['Weighted_Mean_Subjectivity_Country']=float()

    for country in dataframe.Country_User.unique():
        if(country == ''):
            dataframe.loc[dataframe.Country_User==country,'Mean_Polarity_Country'] = ''
            dataframe.loc[dataframe.Country_User==country,'Mean_Subjectivity_Country'] = ''
            dataframe.loc[dataframe.Country_User==country,'Mean_Reputation_Country'] = ''
        else:
            dataframe.loc[dataframe.Country_User==country,'Mean_Polarity_Country'] =100 * dataframe[dataframe.Country_User==country].Polarity.mean()
            dataframe.loc[dataframe.Country_User==country,'Weighted_Mean_Polarity_Country'] =(1000000 * dataframe[dataframe.Country_User==country].Polarity.mean() * dataframe[dataframe.Country_User==country].Total_Tweets_Country.mean())/dataframe['Total_Tweets_Country'].sum()     
            dataframe.loc[dataframe.Country_User==country,'Mean_Subjectivity_Country'] =100 * dataframe[dataframe.Country_User==country].Subjectivity.mean()
            dataframe.loc[dataframe.Country_User==country,'Weighted_Mean_Subjectivity_Country'] =(1000000 * dataframe[dataframe.Country_User==country].Subjectivity.mean() * dataframe[dataframe.Country_User==country].Total_Tweets_Country.mean())/dataframe['Total_Tweets_Country'].sum()     
            dataframe.loc[dataframe.Country_User==country,'Mean_Reputation_Country'] =100 * dataframe[dataframe.Country_User==country].Reputation.mean()

    return dataframe

def meanSentimentsUsState(dataframe):
    dataframe['Mean_Polarity_USA_State']=float()
    dataframe['Mean_Subjectivity_USA_State']=float()
    dataframe['Mean_Reputation_USA_State']=float()
    dataframe['Weighted_Mean_Polarity_USA_State']=float()

    for us_state in dataframe.USA_State_User.unique():
        if(us_state == ''):
            dataframe.loc[dataframe.USA_State_User==us_state,'Mean_Polarity_USA_State'] = ''
            dataframe.loc[dataframe.USA_State_User==us_state,'Mean_Subjectivity_USA_State'] = ''
            dataframe.loc[dataframe.USA_State_User==us_state,'Mean_Reputation_USA_State'] = ''
        else:
            dataframe.loc[dataframe.USA_State_User==us_state,'Mean_Polarity_USA_State'] =100 * dataframe[dataframe.USA_State_User==us_state].Polarity.mean()
            dataframe.loc[dataframe.USA_State_User==us_state,'Weighted_Mean_Polarity_USA_State'] =(1000000 * dataframe[dataframe.USA_State_User==us_state].Polarity.mean() * dataframe[dataframe.USA_State_User==us_state].Total_Tweets_USA_State.mean())/dataframe['Total_Tweets_USA_State'].sum() 
            dataframe.loc[dataframe.USA_State_User==us_state,'Mean_Subjectivity_USA_State'] =100 * dataframe[dataframe.USA_State_User==us_state].Subjectivity.mean()
            dataframe.loc[dataframe.USA_State_User==us_state,'Mean_Reputation_USA_State'] =100 * dataframe[dataframe.USA_State_User==us_state].Reputation.mean()

    return dataframe

def worldMap(polarity,country_code):
    from plotly import plotly
    import simplejson as json
    scl_world = [[-100,"rgb(5, 10, 172)"],\
           [0,"rgb(40, 60, 190)"],[200,"rgb(70, 100, 245)"],[400,"rgb(90, 120, 245)"],[600,"rgb(106, 137, 247)"],[800,"rgb(220, 220, 220)"]]

    graphs = [dict(data = [dict(type = 'choropleth',locations = country_code,z = polarity,text = country_code,
                                colorscale = scl_world,
                                autocolorscale = False, reversescale = True,
                                marker = dict( line = dict(color = 'rgb(86,81,81)', width = 1)), 
                                colorbar = dict(title = 'Polarity'))],
                   layout = dict(title = 'World Map (Polarity)',geo = dict(showframe = True,showcoastlines = True,projection = dict(type = 'Mercator')),
                                 autosize=False, width=1200, height=700,
                                 margin=dict(l=0,r=10,b=80,t=90,pad=0)))]
    world_map_id = ['World_Map']
    
    world_map_json = json.dumps(graphs, cls=plotly.plotly.utils.PlotlyJSONEncoder)
    return world_map_json, world_map_id

def UsMapPlot(polarity,us_state_code):
    from plotly import plotly
    import simplejson as json

    scl_usa = [[0.0, 'rgb(242,240,247)'],[500, 'rgb(218,218,235)'],[1000, 'rgb(188,189,220)'],\
            [2000, 'rgb(158,154,200)'],[2000, 'rgb(117,107,177)'],[3000, 'rgb(84,39,143)']]
    graphs = [dict( data = [dict(type='choropleth',colorscale = scl_usa, autocolorscale = False,reversescale = True,
                                 locations = us_state_code, z = polarity, locationmode = 'USA-states',
                                 marker = dict(line = dict (color = 'rgb(255,255,255)',width =1)),colorbar = dict(title = "Map Plot"))],
                   layout = dict(title = 'USA Map (Poalrity)',geo = dict(showframe = True,scope='usa',projection=dict(type='albers usa' ),
                                                                        showlakes = True,lakecolor = 'rgb(255, 255, 255)'),
                                 autosize=False, width=1200, height=700, margin=dict(l=0,r=10,b=80,t=90,pad=0)))]
    usa_map_id = ['Map']
    usa_map_json = json.dumps(graphs, cls=plotly.plotly.utils.PlotlyJSONEncoder)
    return usa_map_json, usa_map_id

def bar_sentiments(polarity,subjectivity,dates):
    from plotly import plotly
    import simplejson as json
    
#==============================================================================
#     trace1 = go.Bar(
#         x=dates,
#         y=polarity,
#         name='Polarity'
#     )
#     trace2 = go.Bar(
#         x=dates,
#         y=subjectivity,
#         name='Subjectivity'
#     )
#     
#     data = [trace1, trace2]
#     layout = go.Layout(
#         barmode='group'
#     )
#==============================================================================
    graphs = [dict(data=[dict(x=dates, y=polarity, type='bar', name='Polarity'),dict(x=dates,y=subjectivity,type='bar',
                    name='Subjectivity'),], layout=dict(autosize=False, width=1800, height=700, margin=dict(l=0,r=10,b=80,t=90,pad=0),showframe = True, title='Bar Plot',barmode='group',bargap=0.10,bargroupgap=0.1))]
    bar_id = ['Bar']
    basic_bar_json = json.dumps(graphs, cls=plotly.plotly.utils.PlotlyJSONEncoder)
    return basic_bar_json,bar_id

def dataSummaryWorld(df):
    import pandas as pd
    Country=[]
    total_tweets_Count =[]
    summary_df = pd.DataFrame(columns=('Country','# Tweets'))
    for country in df.Country_User.unique():
        Country.append(country)
        total_tweets_Count.append(int(df[df.Country_User==country]['Total_Tweets_Country'].mean()))
    
    summary_df['Country'] = Country
    summary_df['# Tweets'] = total_tweets_Count
                                  
    #df.groupby(country).mean()
    summary_df = summary_df.sort_values(by=['Country']).reset_index(drop=True)
    return summary_df

def dataSummaryCountry(df, countryName):
    #Check Renaming refactoring
    import pandas as pd
    columnNameLocation = str(countryName) +'_State'
    columnNameTweets = '# Tweets'
    country_state=[]
    total_tweets_count_state =[]
    summary_df_country = pd.DataFrame(columns=(columnNameLocation,columnNameTweets))
    for state in df[columnNameLocation+'_User'].unique():
        if(state!= ''):
           country_state.append(state)
           total_tweets_count_state.append(int(df[df[columnNameLocation+'_User']==state]['Total_Tweets_USA_State'].mean()))
    
    summary_df_country[columnNameLocation] = country_state
    summary_df_country[columnNameTweets] = total_tweets_count_state
                                  
    #df.groupby(country).mean()
    summary_df_country = summary_df_country.sort_values(by=[columnNameLocation]).reset_index(drop=True)
    return summary_df_country

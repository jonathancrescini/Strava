# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 21:13:54 2021

@author: jonat
"""

import requests
import urllib3
import os
import pandas as pd
from pandas import json_normalize
from datetime import datetime

# get directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# load API keys
keys = pd.read_csv('StravaApiPwd.txt', sep= ' ', header=None)
AccessToken = keys.iloc[0,1]
RefreshToken = keys.iloc[1,1]
ClientID = keys.iloc[2,1]
ClientSecret = keys.iloc[3,1]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"

payload = {
    'client_id': ClientID,
    'client_secret': ClientSecret,
    'refresh_token': RefreshToken,
    'grant_type': "refresh_token",
    'f': 'json'
}

print("Requesting Token...\n")
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
print("Access Token = {}\n".format(access_token))

header = {'Authorization': 'Bearer ' + access_token}
for page in range(1, 5):
    print("Retrieving your activities: {0:2.0f}% completed".format(page/4*100))
    param = {'per_page': 200, 'page':page} # , 'page': [1,2]
    my_dataset = requests.get(activites_url, headers=header, params=param).json()
    
    if len(my_dataset) != 0:
        dfs = []
        # switch data to a df
        df = json_normalize(my_dataset)
        dfs.append(df)
        #if page == 1:
        #    activities = df
        #else:
        #    activities = pd.concat([activities, df], ignore_index = True)
    else:
        
        break
    
activities = pd.concat(dfs) 
# save activities for futher use
activities.to_csv('activities.csv')

# select runs only
runs = activities.query('type in("Run", "Hike")')

# select only columns relevant for runs
cols = ['id', 'name', 'distance', 'moving_time', 'elapsed_time',
       'total_elevation_gain', 'type', 'workout_type', 'start_date',
       'start_date_local', 'timezone', 'utc_offset',
       'start_latlng', 'end_latlng', 'location_city', 'location_state',
       'location_country', 'start_latitude', 'start_longitude',
       'achievement_count', 'kudos_count', 'comment_count', 'athlete_count',
       'photo_count', 'trainer', 'commute', 'manual', 'private', 'visibility',
       'flagged', 'gear_id', 'from_accepted_tag', 'upload_id_str',
       'average_speed', 'max_speed', 'average_cadence', 'average_temp',
       'has_heartrate', 'average_heartrate', 'max_heartrate',
       'heartrate_opt_out', 'display_hide_heartrate_option', 'elev_high',
       'elev_low', 'pr_count', 'total_photo_count', 'has_kudoed',
       'suffer_score', 'map.id',
       'map.summary_polyline', 'map.resource_state']

runs = runs[cols]

# change col dtypes
runs['start_date_local'] = pd.to_datetime(runs['start_date_local'])



# save runs for further use
runs.to_csv('runs.csv', index=False)

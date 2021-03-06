### Imports
import requests
from bs4 import BeautifulSoup as BS
import json
import datetime
import pandas as pd
from pathlib import Path
import os



### Global Variables

# get trending website info and api info
url = 'https://www.youtube.com/feed/trending'
api_url = 'https://www.googleapis.com/youtube/v3/videos?id=here&part=snippet,statistics,recordingDetails&key=AIzaSyA_ltEFFYL4E_rOBYkQtA8aKHnL5QR_uMA'
td = BS(requests.get(url).content, 'html.parser').find_all('li', {'class': 'expanded-shelf-content-item-wrapper'})
# time info
time_now = datetime.datetime.now()
# desired column names
col_list = ['title', 'ID', 'url', 'channel', 'datetime', 'length', 'viewCount', 'likeCount', 'dislikeCount', 'commentCount', 'oneDayEnd']
# file names
old_file_name = Path('Trending Videos.csv')
new_file_name = Path('Trending Videos_new.csv')



### Define Functions
def get_info():
    for i in range(10):
        # retrieve only non-live videos
        if td[i].find_all('span', {'class':'yt-badge yt-badge-live'}) == []:
            i_id = td[i].find('a').get('href')[-11:]
            i_api = requests.get(api_url.replace('here', i_id)).json()
            # get video upload time and transfer to EST time
            i_datetime = pd.to_datetime(i_api['items'][0]['snippet']['publishedAt']) - pd.Timedelta('4 hours')
            # reteieve only shorter-than-1day videos
            if (time_now - i_datetime).days < 1:
                videos['ID'].append(i_id)
                i_url = 'www.youtube.com' + td[i].find('a').get('href')
                videos['url'].append(i_url)
                videos['length'].append(td[i].find('span',{'class':'video-time'}).get_text())
                videos['title'].append(i_api['items'][0]['snippet']['title'])
                videos['channel'].append(i_api['items'][0]['snippet']['channelTitle'])
                videos['datetime'].append(i_datetime)
                # if there is 'statistics'
                try:
                    if_s_exists = i_api['items'][0]['statistics']['viewCount']
                except KeyError:
                    if_s_exists = 'gotothatpage'
                # if 'statistics' is unavailable
                if if_s_exists == 'gotothatpage':
                    i_tough = BS(requests.get('http://' + i_url).content, 'html.parser')
                    videos['viewCount'].append(i_tough.find('div', {'class':'watch-view-count'}).get_text()[:-6].replace(',',''))
                    videos['likeCount'].append(i_tough.find('button', {'title':'Unlike'}).get_text().replace(',',''))
                    videos['dislikeCount'].append(i_tough.find('button', {'title':'I dislike this'}).get_text().replace(',',''))
                    videos['commentCount'].append('')
                    videos['oneDayEnd'].append(0)
                # if 'statistics' is available
                else:
                    videos['viewCount'].append(i_api['items'][0]['statistics']['viewCount'])
                    videos['likeCount'].append(i_api['items'][0]['statistics']['likeCount'])
                    videos['dislikeCount'].append(i_api['items'][0]['statistics']['dislikeCount'])
                    videos['commentCount'].append(i_api['items'][0]['statistics']['commentCount'])
                    videos['oneDayEnd'].append(0)
                    
def to_pd(videos):
    df = pd.DataFrame(videos)
    df = df[col_list]
    return df

def to_csv(df):
    df.to_csv('Trending Videos.csv', encoding='utf-8')

def add_new(df):
    # clean df
    try:
        df = df.drop('Unnamed: 0', 1)
    except:
        df = df
    # a list containing all current IDs
    tmp_id_list = []
    for df_id in df['ID']:
        tmp_id_list.append(df_id)
    # see if new ones in list
    for i in range(10):
        # retrieve only non-live videos
        if td[i].find_all('span', {'class':'yt-badge yt-badge-live'}) == []:
            i_id = td[i].find('a').get('href')[-11:]
            if i_id not in tmp_id_list:
                i_api = requests.get(api_url.replace('here', i_id)).json()
                i_datetime = pd.to_datetime(i_api['items'][0]['snippet']['publishedAt']) - pd.Timedelta('4 hours')
                if (time_now - i_datetime).days < 1:
                    i_url = 'www.youtube.com' + td[i].find('a').get('href')
                    # if there is 'statistics'
                    try:
                        if_s_exists = i_api['items'][0]['statistics']['viewCount']
                    except KeyError:
                        if_s_exists = 'gotothatpage'
                    if if_s_exists == 'gotothatpage':
                        i_tough = BS(requests.get('http://' + i_url).content, 'html.parser')
                        df.loc[-1] = [i_api['items'][0]['snippet']['title'], 
                                      i_id, 
                                      i_url, 
                                      i_api['items'][0]['snippet']['channelTitle'],
                                      i_datetime,
                                      td[i].find('span',{'class':'video-time'}).get_text(),
                                      i_tough.find('div', {'class':'watch-view-count'}).get_text()[:-6].replace(',',''),
                                      i_tough.find('button', {'title':'Unlike'}).get_text().replace(',',''),
                                      i_tough.find('button', {'title':'I dislike this'}).get_text().replace(',',''),
                                      '',
                                      0]
                    else:
                        df.loc[-1] = [i_api['items'][0]['snippet']['title'], 
                                      i_id, 
                                      i_url, 
                                      i_api['items'][0]['snippet']['channelTitle'],
                                      i_datetime,
                                      td[i].find('span',{'class':'video-time'}).get_text(),
                                      i_api['items'][0]['statistics']['viewCount'],
                                      i_api['items'][0]['statistics']['likeCount'],
                                      i_api['items'][0]['statistics']['dislikeCount'],
                                      i_api['items'][0]['statistics']['commentCount'],
                                      0]
                    df = df.reset_index(drop=True)
    return df

# run add_new before check_old
def check_old(df):
    for df_time in df['datetime']:
        df_time_index = pd.Index(df['datetime']).get_loc(df_time)
        df_time = pd.to_datetime(df_time)
        if df.oneDayEnd.iloc[df_time_index] == 0:
            if (time_now - df_time).days >= 1:
                i_api = requests.get(api_url.replace('here', df.ID.iloc[df_time_index])).json()
                i_url = df.url.iloc[df_time_index]
                # update 
                # if there is 'statistics'
                try:
                    if_s_exists = i_api['items'][0]['statistics']['viewCount']
                except KeyError:
                    if_s_exists = 'gotothatpage'
                if if_s_exists == 'gotothatpage':    
                    i_tough = BS(requests.get('http://' + i_url).content, 'html.parser')
                    df.set_value(df_time_index, 'viewCount', i_tough.find('div', {'class':'watch-view-count'}).get_text()[:-6].replace(',',''))
                    df.set_value(df_time_index, 'likeCount', i_tough.find('button', {'title':'Unlike'}).get_text().replace(',',''))
                    df.set_value(df_time_index, 'dislikeCount', i_tough.find('button', {'title':'I dislike this'}).get_text().replace(',',''))
                    # no need for comment since alreay '' in this case
                    df.set_value(df_time_index, 'oneDayEnd', 1)
                else:    
                    df.set_value(df_time_index, 'viewCount', i_api['items'][0]['statistics']['viewCount'])
                    df.set_value(df_time_index, 'likeCount', i_api['items'][0]['statistics']['likeCount'])
                    df.set_value(df_time_index, 'dislikeCount', i_api['items'][0]['statistics']['dislikeCount'])
                    df.set_value(df_time_index, 'commentCount', i_api['items'][0]['statistics']['commentCount'])
                    df.set_value(df_time_index, 'oneDayEnd', 1)
    return df



### Run All

# A backup file 'Trending Videos.csv' is created and updated everytime so that we always has a newest file and a last version.
# 'Trending Videos_new.csv' is my final product.

# if an initial doesn't exist, create one
if not old_file_name.is_file():
    videos = {'title':[],
          'ID':[],
          'url':[],
          'channel':[],
          'datetime':[],
          'length':[],
          'viewCount':[],
          'likeCount':[],
          'dislikeCount':[],
          'commentCount':[],
          'oneDayEnd':[]}
    get_info()
    to_csv(to_pd(videos))

if not new_file_name.is_file():
    df = pd.read_csv('Trending Videos.csv', encoding='utf-8')
    df = add_new(df)
    df = check_old(df)
    df.to_csv('Trending Videos_new.csv', encoding='utf-8')
else:
    # update two files
    df = pd.read_csv('Trending Videos_new.csv', encoding='utf-8')
    df = add_new(df)
    df = check_old(df)
    backup = pd.read_csv('Trending Videos_new.csv', encoding='utf-8')
    os.remove('Trending Videos.csv')
    backup.to_csv('Trending Videos.csv', encoding='utf-8')
    os.remove('Trending Videos_new.csv')
    df.to_csv('Trending Videos_new.csv', encoding='utf-8')
# -*- coding: utf-8 -*-

### Imports
import requests
from bs4 import BeautifulSoup as BS
import re
import codecs
import pandas as pd
import time
from datetime import datetime



### Define Functions

## get url_list
def get_url_list(mid):
    base_url = 'http://space.bilibili.com/ajax/member/getSubmitVideos?page='
    url_list = []
    no_page = int(re.findall('pages":(\d+)', str(requests.get('http://space.bilibili.com/ajax/member/getSubmitVideos?page=1&mid=%s' % mid).content))[-1])
    for i in range(1, no_page+1):
        url_list.append(base_url + '%d&mid=%s' % (i,mid))
    return url_list

## get info
def get_info(url_list):
    ## spider 1/3
    print('initiating spider 1/3...')
    videos = []
    index = 0
    total_videos = re.findall('count":(\d+)', str(requests.get('http://space.bilibili.com/ajax/member/getSubmitVideos?page=1&mid=%s' % mid).content))[-1]
    for url in url_list:
        url_page = codecs.decode(requests.get(url).content, 'unicode_escape')
        spider1_1 = re.findall('aid":(\d+).{1,50}title":"(.{1,80})","sub.{1,50}play":(\d+),"review":(\d+),"video_review":(\d+),"favorites":(\d+)', url_page)
        spider1_2 = re.findall('created":([\d:]+),.{1,120}length":"([\d:]+)', url_page)    
        spider1_2_index = 0 # index of spider1_2，reset every big loop
        for tuples in spider1_1:
            videos.append(dict())
            videos[index]['aid'] = tuples[0]
            videos[index]['title'] = tuples[1]
            videos[index]['play'] = tuples[2]
            videos[index]['review'] = tuples[3]
            videos[index]['danmaku'] = tuples[4]
            videos[index]['favorites'] = tuples[5]
            videos[index]['date'] = datetime.fromtimestamp( int(spider1_2[spider1_2_index][0]) ).strftime('%Y-%m-%d %H:%M:%S')[:10]
            videos[index]['time'] = datetime.fromtimestamp( int(spider1_2[spider1_2_index][0]) ).strftime('%Y-%m-%d %H:%M:%S')[11:]
            videos[index]['length'] = spider1_2[spider1_2_index][1]
            index += 1
            spider1_2_index += 1
            print(str(index) + '/' + total_videos + ' information collected from ' + url)
        print('page' + str(url_list.index(url) + 1) + 'completed')
    # clean 'title'
    for i in videos:
        i['title'] = i['title'].replace('\\/','/')
    print('spider 1/3 finished')
    ## spider 2/3
    print('initiating spider 2/3...')
    spider2_url = 'http://api.bilibili.com/archive_stat/stat?aid='
    for j in videos:
        aid = j['aid']
        url = spider2_url + aid # type(aid) = aid, thus no need to convert it
        # get page and prevent from ConnectionError
        page = " "
        while page == " ":
        	try:
        		page = requests.get(url)
        	except:
        		print("Connection refused by the server...Let me sleep for 5 seconds...ZZzzzz...")
        		time.sleep(2)
        		print("Let me continue...")
        		continue
        coin = re.findall('coin":(\d+)', str(page.content))[0]
        j['coin'] = coin
        print(str(videos.index(j)+1) + '/' + total_videos + ' information collected from ' + url) 
    print('spider 2/3 finished')
    ## spider 3/3
    print('initiating spider 3/3...')
    spider3_url = 'http://www.bilibili.com/video/av'
    for k in videos:
        aid = k['aid']
        url = spider3_url + aid
        k['url'] = url
        print(str(videos.index(k)+1) + '/' + total_videos + ' information collected from ' + url)
    print('spider 3/3 finished')
    ## finish
    return videos


## put into pandas
def into_pandas(videos):
    df_videos = pd.DataFrame(videos)
    # change columns order
    df_videos = df_videos[['aid','title', 'url', 'date','time','length', 'play', 'danmaku', 'review', 'favorites', 'coin']]
    # change object type to int
    df_videos['play'] = df_videos['play'].astype(int)
    df_videos['danmaku'] = df_videos['danmaku'].astype(int)
    df_videos['review'] = df_videos['review'].astype(int)
    df_videos['favorites'] = df_videos['favorites'].astype(int)
    df_videos['coin'] = df_videos['coin'].astype(int)
    print('Success putting data into Pandas')
    return df_videos

## export to csv file
# notice: to open it in excel, please open in notepad first, save it, and then open in excel
def export_csv(df):
    # get current time
    time = str(datetime.now())[:10] + '_' + str(datetime.now())[11:13] + '\'' + str(datetime.now())[14:16] + '\'' + str(datetime.now())[17:19]
    # export
    filename = 'stat_%s_%s.csv' % (mid, time)
    df.to_csv(filename, encoding='utf-8')



### Run All - input mids
"""
## get num of broadcasters
num = input("Enter the number of broadcasters to collect: ")
num = int(num)

## get a list of mid
mid_list = []
for i in range(num):
    mid = input("Enter {0}/{1} user's id: ".format(i, num))
    if mid.isdigit() == True and len(mid) <=9:
        print('User ID:', mid)
        mid = str(mid)
    else:
        mid = input("Last chance, please enter a valid ID: ")
        if mid.isdigit() == True and len(mid) <=9:
            print('User ID:', mid)
        else:
            print('Application Terminated. Please run again.')
            mid = 0
    mid_list.append(mid)

## call functions
for mid in mid_list:
    if mid != 0:
        # run all functions
        print('Application Running...')
        export_csv(into_pandas(get_info(get_url_list(mid))))
        print('\nA csv file containing information of all videos of the specified user id has been created in your current directory, please check!')

"""



### Run All - auto

## Mid List - details in the last section
mid_list = ['43536', '423895', '433351', '16693558', '3607081', '742470', '2745073']
# test: mid_list = ['742470', '2745073']

## call functions
for mid in mid_list:
    if mid != 0:
        # run all functions
        print('Application Running... for {0}/{1} user'.format(mid_list.index(mid)+1, len(mid_list)))
        export_csv(into_pandas(get_info(get_url_list(mid))))
        print('\nA csv file containing information of all videos of the specified user id has been created in your current directory, please check!')



### Mid List 

# 黑桐谷歌： 43536
# 王老菊: 423895
# 老E： 433351
# Virgoo Team: 16693558
# 球魂： 3607081
#　冰冷之海：　742470
# 氪金氪金克： 2745073

# 暴漫： 883968
# -*- coding: utf-8 -*-

### Imports
import requests
from bs4 import BeautifulSoup as BS
import os


### Get Url List

base_url = 'http://hatsuneyuko.tumblr.com/page/1'

# get page_length
page_length = int(BS(requests.get(base_url).content, 'html.parser').find('a', {'class':'next'}).get('data-total-pages'))
# get list
url_list = []
for i in range(1, page_length+1):
    url_list.append('http://hatsuneyuko.tumblr.com/page/%d' % i)
# get page
url_page = []
for i in range(page_length):
    url_page.append(BS(requests.get(url_list[i]).content, 'html.parser'))



### Define Functions

## Spiders
# spider1 - multipic pics
def spider1(url_page):
    # use dict to create a dict of pages, each has an empty list
    page_iframe = {}
    for i in range(page_length):
        page_iframe['page%d' % (i+1)] = []
    # put each page's if_scr to the list
    for i,k in enumerate(url_page):
        for j in k.find_all('iframe'):
            if j.has_attr('src'):
                page_iframe['page%d' % (i+1)].append(j.get('src'))
        page_iframe['page%d' % (i+1)] = [s for s in page_iframe['page%d' % (i+1)] if 'false' in s]
    # 此dict太复杂，换一个整体的list
    id_li = {}
    for i in page_iframe:
        for j in page_iframe[i]:
            id_li[j.split('/')[4]] = j
    for i in id_li:
        soup = BS(requests.get(id_li[i]).content, 'html.parser').find_all('img')
        soup = [s.get('src') for s in soup]
        id_li[i] = soup
    return id_li
# spider2 - non_iframe_pics
def spider2(url_page):
    spider2_list = []
    for i in range(page_length):
        # 如果直接 append blah的话，spider2+list会是一个包含str和list的list
        l = [s for s in url_page[i].find_all('img') if s.has_attr('height')]
        for j in l:
            spider2_list.append(j)
    non_iframe_pics = {}
    for i in spider2_list:
        non_iframe_pics[i.get('alt')] = i.get('src')
    return non_iframe_pics
# spider3 - videos
def spider3(url_page):
    # video_urls
    video_list = []
    for i in range(page_length):
        temp = url_page[i].find_all('iframe', {'class':'embed_iframe tumblr_video_iframe'})
        for j in temp:
            video_list.append(j)
    video_list = [s.get('src') for s in video_list]
    # find videos
    video_list_deep = []
    for i in range(len(video_list)):
        soup = BS(requests.get(video_list[i]).content, 'html.parser').find_all('video')
        for j in soup:
            video_list_deep.append(j)
    for i in range(len(video_list_deep)):
        video_list_deep[i] = video_list_deep[i].find('source').get('src')
    # store in a dict
    videos = {}
    for i in range(len(video_list_deep)):
        videos[video_list_deep[i].split('/')[5]] = video_list_deep[i]
    return videos

## Download
def spider_download(spider1, spider2, spider3):
    # create a "pic" folder
    os.makedirs('Youmu_download')
    # download spider1
    for s1 in spider1:
        os.makedirs('Youmu_download\\pic\\' + s1) # 根据 post_id 创建文件夹
        # 解析每个 post_id 的网址，下载到对应文件夹
        for s11, s12 in enumerate(spider1[s1]): # b=index
            s1_img = requests.get(s12).content
            print('downloading a new picture from spider1...')
            with open('Youmu_download\\pic\\' + s1 + '\\%s.jpg' % (s11+1), 'wb') as handler:
                handler.write(s1_img)
    # download spider2
    index = 0
    os.makedirs('Youmu_download\\pic\\single_pics')
    for s2 in spider2:
        s2_img = requests.get(spider2[s2]).content
        print('downloading a new picture from spider2...')
        with open('Youmu_download\\pic\\single_pics\\' + str(index) + spider2[s2][-4:], 'wb') as  handler:
            handler.write(s2_img)
        index += 1
    # download spider3
    os.makedirs('Youmu_download\\videos\\')
    for s3 in spider3:
        mp4 = requests.get(spider3[s3]).content
        print('downloading a new video from spider3...')
        with open('Youmu_download\\videos\\' + '\\%s.mp4' % (s3), 'wb') as  handler:
            handler.write(mp4)
    print('downloading finished')



### Run All
spider_download(spider1(url_page), spider2(url_page), spider3(url_page))

# spider main code for paste 
'''
for web from these two sites:
'https://justpaste.it',
'https://pastebin.com',
'''
import requests
import bs4
import pandas as pd
import json
import time
import random
import unidecode
import re
from dateutil.parser import *

headers = {
    'User-Agent':your_agent
    # ,'Connection':'close'
}

def get_bs4_obj(url):
    # creation session
    rs = requests.session()
    # rs.keep_alive = False
    html = rs.get(url, headers = headers)
    obj = bs4.BeautifulSoup(html.text, 'html.parser')
    return obj

def get_by_splash(url):
    infos = list()
    html = requests.get('http://localhost:8050/render.html',
             params={'url': url, 'wait': 0.5})
    obj = bs4.BeautifulSoup(html.text, 'html.parser')
    info_obj = obj.find('div', class_='articleBarLeftLogin')
    try:
        user_name = info_obj.find('a', class_='articlePremiumUserLink').text
        date = info_obj.find_all('span', class_='userNameSubLineArticle')[1].text.split('· ')[1]
    except:
        user_name = ''
        date = info_obj.find_all('span', class_='userNameSubLineArticle')[0].text.split('· ')[1]
    # infos 
    try:
        date = unidecode.unidecode(date)
        infos.append(parse(date))
    except:
        infos.append('')
    try:
        views = obj.find('span', class_='footerDate').text
        views = unidecode.unidecode(views)
        infos.append(views.split(' ')[0])
    except:
        infos.append('')
    infos.append('') #expire date
    return user_name, infos


def get_page_info(user_name, infos, post_title, posts):
    infos[1] = infos[1].replace(',','')
    page_info = dict()
    page_info['user_name'] = user_name
    page_info['date'] = infos[0]
    page_info['views'] = int(infos[1])
    page_info['expire'] = infos[2]
    page_info['post_title'] = post_title
    page_info['posts'] = posts
    return page_info

def clean_post(text):
    text = unidecode.unidecode(text)
    regex = re.compile(r'[\n\r\t]')
    text = regex.sub(" ", text)
    return text

def parse_pastebin(obj):
    ## get meta data
    try:
        info_bar = obj.find('div', class_='info-bar')
        info_bottom = info_bar.find('div', class_='info-bottom')
        list_info_bottom = info_bottom.find_all('div')
        infos_list = [info.text.split("\n")[1].replace(' ','') for info in list_info_bottom]
        user_name = infos_list[0]
        infos = infos_list[1:]
        infos[0] = parse(infos[0])
    except:
        info_bar = ''
        info_bottom = ''
        user_name = ''
        list_info_bottom = ''
        infos = ''
    ## get posts
    try:
        post_title = info_bar.h1.text
    except:
        post_title = ''
    # method 1
    try:
        posts = obj.find_all('div', class_='de1')
        posts = [clean_post(p.text) for p in posts]
    except:
        try:
            posts = obj.textarea.text
        except:
            posts = ''
    return user_name, infos, post_title, posts

def parse_justpaste(url, obj): #splash version
    ## get meta data
    user_name, infos = get_by_splash(url)
    ## get posts
    try:
        post_title = obj.find('div', class_='text-center').text
        post_title = unidecode.unidecode(post_title)
    except:
        post_title = ''
    try:
        posts_obj = obj.find('div', {'id':'articleContent'})
        posts = [clean_post(p.text) for p in posts_obj.find_all('p')]
    except:
        try:
            posts_obj.text
        except:
            posts = ''
    return user_name, infos, post_title, posts

def main(url):
    try:
        obj = get_bs4_obj(url)
    except Exception as e:
        print("get_bs4_obj faliure:",e)

    if 'justpaste' in url:
        user_name, infos, post_title, posts = parse_justpaste(url, obj)
    elif 'pastebin' in url:
        user_name, infos, post_title, posts = parse_pastebin(obj)
    else:
        pass
    
    page_info = get_page_info(user_name, infos, post_title, posts)
    return page_info
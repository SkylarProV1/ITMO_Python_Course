import requests
from bs4 import BeautifulSoup
import html5lib
import time
import random


def extract_news(parser):
    """ Extract news from a given web page """
    news_list = []
    urls=list()
    
    title = parser.findAll('a',class_='storylink')
    url = parser.findAll('td',class_='title')
    score=parser.findAll('span',class_='score')
    name=parser.findAll('a',class_='hnuser')
    comment=parser.findAll('td',class_='subtext')
    
    for i in url:
        try:
            if i.a.get('href')[:2]=='ht':
                urls.append(i.a.get('href'))
        except AttributeError as e:
            continue
        
    for i in range(30):
        ans={'author': '',
        'comments':'',
        'points': '',
        'title': '',
        'url': ''}
        try:
            ans.update({'author':name[i].text})
            ans.update({'comments':comment[i].findAll('a')[-1].text.split()[0]})
            ans.update({'points':score[i].text.split(' ')[0]})
            ans.update({'title':title[i].text})
            ans.update({'url':urls[i]})
            news_list.append(ans)
        except IndexError as e:
            news_list.append(ans)
            continue
    return news_list


def extract_next_page(parser):
    """ Extract next page URL """
    tbl_list = parser.table.findAll('table')
    return tbl_list[1].findAll('td')[-1].a.get('href')

def get_news(url, n_pages=1):
    """ Collect news from a given web page """
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html5lib")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)
        time.sleep(random.randint(10,15))
        n_pages -= 1
    return news


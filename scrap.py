import requests
from bs4 import BeautifulSoup
# import urllib2
import time
import json

baseurl = 'https://fourminutebooks.com/book-summaries/'
CACHE_FILENAME = "cache.json"
CACHE_DICT = {}


##################
##  Scrapping   ##
##################
class Book:

    def __init__(self, title, summary, amazon):
        self.title = title
        self.summary = summary
        self.amazon = amazon


def get_recipe_instance(url_text):
    '''Make an instances from the site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a recipe page in recipepuppy.com
    
    Returns
    -------
    instance
        a national site instance
    '''
    soup = BeautifulSoup(url_text, 'html.parser')
    div_right = soup.find_all('div', class_='w4pl-inner')
    # book_list = []

    div_right

    # for index, i in enumerate(div_right, 1):
    #     try:
    #         name = i.find('h3').text
    #     except:
    #         name = 'None'

    #     try:
    #         url = i.find('div', class_='url').text.split(' ')[0]
    #     except:
    #         url = 'None'

    #     try:
    #         website = i.find('a')['href']
    #     except:
    #         website = 'None'
    #     try:
    #         image = i.find('img', class_='thumb')['src']
    #     except:
    #         image = 'None'

        # book_list.append(Book(title))

    # return book_list

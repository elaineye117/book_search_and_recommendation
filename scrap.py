import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://fourminutebooks.com/book-summaries/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# Scrape using beatifulsoup
result = requests.get(url, headers=headers)
soup = BeautifulSoup(result.content, "html.parser")
div_right = soup.find_all('div', class_='w4pl-inner')

#Obtain Summary for each book
booklist = []
for a in soup.find_all('a',href = True):
    booklist.append(a['href'])
booklisturl = booklist[70:910]
summaries = []

def get_summary(url):
    link = url
    result_page = requests.get(link, headers=headers)
    soup_page = BeautifulSoup(result_page.content, "html.parser")
    table = soup_page.find('div', class_='entry-content')

    text = table.find('p')
    summary = text.get_text()

    return summary

# Use tqdm to see the scrapping status
from tqdm import tqdm_notebook as tqdm
for sum in tqdm(booklisturl):
    summaries.append(get_summary(sum))
    
# save summary into datafram
summary = pd.DataFrame(summaries)   

# clean summary by removing same first words:'1-Sentence-Summary: '
summary['response'] = summary['response'].str.replace('1-Sentence-Summary: ', '', regex=True).replace('1-Sentence-Summary:', '', regex=True)

# Rename column name
summary = summary.rename(columns={0: "response"})

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


# Scrap book name from the website

def get_title(url):
    link = url
    result_page = requests.get(link, headers=headers)
    soup_page = BeautifulSoup(result_page.content, "html.parser")
    table = soup_page.find('div', class_='entry-content')
    p = table.find('p')
    try:     
        title = p.find('a').get_text()
    except AttributeError:
        title = "no title"
    return title

for link in tqdm(booklisturl):
    titles.append(get_title(link))
   

books = books.rename(columns={0: "book"})



# Obtain category for each book
def get_cat(url):
    book_classes = []
    link = url
    result_page = requests.get(link, headers=headers)
    soup_page = BeautifulSoup(result_page.content, "html.parser")
    table = soup_page.find('div', class_='entry-meta')
    categories = table.find_all('a', rel="category tag")
    for i in categories:
        a = i.get_text()
        book_class.append(a) 
    return book_classes


class_ = []
for link in tqdm(booklisturl):
    class_.append(get_cat(link))
    
class_ = []
for j in class_:
    j = str(j)
    classes.append(j)
 
# save class into a datafram and save it into a csv file
classs = pd.DataFrame(classes)

category = list(df['book_category'])
classs.to_csv("BooksData3.csv")

# Annotation!!!

df = pd.read_csv("BooksData.csv")
category = list(df['book_category'])

point = 0
annotation = []
for i in tqdm(category):
    a = 0
    if 'Happiness' in i:
        a += 1
    elif 'Self Improvement' in i:
        a += 1
    elif 'Health'in i:
        a += 1
    elif 'Motivation' in i:
        a += 0.5
    elif 'Career' in i:
        a += 0.5
    #4/5 = 0.8, 0.8x3=2.4
    if a > 2.4:
        point = 3
    elif a < 1.6 and a > 0.8:
        point = 2
    elif a > 0 and a< 0.8:
        point = 1
    else:
        point = 0
    annotation.append(point)
   
annotation = pd.DataFrame(annotation)

annotation.to_csv('annotation.csv')

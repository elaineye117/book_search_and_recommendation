from bs4 import BeautifulSoup
import requests

url = 'https://fourminutebooks.com/10-days-to-faster-reading-summary/'

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
result = requests.get(url, headers=headers)
# print(result.content.decode())

soup = BeautifulSoup(result.content, "html.parser")

div_right = soup.find_all('div', class_='w4pl-inner')

# for index, i in enumerate(div_right, 1):
#     try:
#         name = i.find('h3').text
#     except:
#         name = 'None'

print(soup)
# Import libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import datetime

start = time.time()
links = []
counter = 0
url = 'https://finviz.com/screener.ashx?v=112'
# Make a GET request to fetch the raw HTML content
content = requests.get(url = url,headers={'user-agent': 'my-app/0.0.1'})
# Parse the html content
soup = BeautifulSoup(content.text, 'html.parser')
page_content = soup.find('td', attrs={'class':'body-table screener_pagination'})
links.append(url)

while (counter < int(page_content.findAll('a',class_='screener-pages')[-1].text)):
    page = url
    # Make a GET request to fetch the raw HTML content
    content = requests.get(url = page, headers={'user-agent': 'my-app/0.0.1'})
    # Parse the html content
    soup = BeautifulSoup(content.text, 'html.parser')
    page_content = soup.find('td', attrs={'class':'body-table screener_pagination'})
    new_url = page_content.find_all('a', attrs={'class':'tab-link'})[-1]['href']
    url = 'https://finviz.com/' + new_url
    links.append(url)
    #print(url)
    counter = counter + 1
df = pd.DataFrame()
df['Links'] = links
df.to_csv('page_links.csv',index=False)
end = time.time()
print('Done! Time taken to scrape links: {}'.format(str(datetime.timedelta(seconds = end-start))))
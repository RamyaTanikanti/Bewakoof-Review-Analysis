# Import libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import datetime

start = time.time()
links = pd.read_csv('page_links.csv')

df = pd.DataFrame()
no = []
ticker = []
company = []
sector = []
industry = []
country = []
mark_cap = []
pe = []
price = []
change = []
volume = []

for link in links['Links']:
    # Make a GET request to fetch the raw HTML content
    content = requests.get(url=link, headers={'user-agent': 'my-app/0.0.1'})
    # Parse the html content
    soup = BeautifulSoup(content.text, 'html.parser')
    # Scraping the table portion
    table = soup.find('div', attrs={'id':'screener-content'})
    # Scraping Tickers
    tickers = table.find_all('a', attrs={'class':'screener-link-primary'})
    for i in tickers:
        ticker.append(i.text)
    # Scraping table values
    values = []
    value = table.find_all('a', attrs={'class':'screener-link'})
    for i in value:
        values.append(i.text)
    # Appending all the scraped values into a list and then into a DataFrame
    cols = [no, company, sector, industry, country, mark_cap, pe, price, change, volume]
    for i,j in zip(list(range(0,10)),cols):
        rng = list(range(0,len(values)))
        rng = rng[i::10]
        for k in rng:
            j.append(values[k])

df['No.'] = no
df['Ticker'] = ticker
df['Company'] = company
df['Sector'] = sector
df['Industry'] = industry
df['Country'] = country
df['MarketCap'] = mark_cap
df['P/E'] = pe
df['Price'] = price
df['Change'] = change
df['Volume'] = volume

end = time.time()
df.to_csv('screener_table_contents.csv',index=False)
print('Done! Time taken to extract table values: {}'.format(str(datetime.timedelta(seconds = end-start))))
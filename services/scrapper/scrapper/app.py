"A simple webscrapping module"

import re
import requests

from typing import Union
from bs4 import BeautifulSoup
from flask import Flask
from requests_cache import CachedSession

app = Flask(__name__)

# app config
app.config['SECRET'] = 'random'

# requests config
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"
}

# requests cache
session = CachedSession('cache', backend='sqlite')

@app.post('/scrap')
def scrap() -> Union[tuple[list[dict], int], tuple[str, int]]:
    "Return list of listing from one page"
    content = get_page_content("https://www.avito.ma/fr/rabat/appartements-%C3%A0_vendre")
    if content:
        res = parse_content(content)
        return res, 200
    return 'Not found', 404


def get_page_content(page_url: str, headers: dict = headers) -> Union[str, None]:
    "Given a url return page content as text"

    content = None

    with session:
        response = session.get(page_url, headers=headers, verify=False)

    if response.status_code == 200:
        content = response.text
        return content

    return content

def parse_content(page_content: str) -> list[dict]:
    "Parse page content and return it as a list of dict"
    
    res = []

    if not page_content:
        return res

    soup = BeautifulSoup(page_content, 'lxml')

    cards = soup.find_all('div', {'data-testid': re.compile('adListCard.')})

    for card in cards:
        # card is a bs4 resultSet
        price = card.find('span', {'data-testid': 'adPrice'})
        if price:
            price = price.find('span', {'dir': 'auto'})
            if price and len(price) > 0:
                price = price.text.replace(',', '')
                price = int(price)
        
        title = card.find('h3', {'data-testid': 'adSubject'}).find('span', {'dir': 'auto'}).text
        url = card.find('a')
        if url:
            url = url.get('href')

        obj = {'title': title, 'price': price, 'url': url}
        res.append(obj)

    return res


if __name__ == '__main__':
    content = get_page_content("https://www.avito.ma/fr/rabat/appartements-%C3%A0_vendre")
    res = parse_content(content)
    breakpoint()
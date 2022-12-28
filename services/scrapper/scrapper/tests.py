""
import re
import requests
import time
import asyncio
import aiohttp

from bs4 import BeautifulSoup

from typing import Callable
from models import Listing, ListingParser
from utils import get_page_content, get_pages_contents, parse_html

PAGES: int = 10


if __name__ == '__main__':
    
    listings = []
    tag = {'url': '//a'}

    urls = [f'https://www.avito.ma/fr/maroc/appartements-%C3%A0_vendre?o={i}' for i in range(PAGES)]
    res = asyncio.run(get_pages_contents(urls))

    urls = []
    for html in res:
        # get the cards
        soup = BeautifulSoup(html, 'lxml')
        cards = soup.find_all('div', {'data-testid': re.compile('adListCard.')})
        for card in cards:
            html = str(card)
            data = parse_html(html, tag)
            urls.append(data['url'])

    res = asyncio.run(get_pages_contents(urls))
    for html in res:
        parser = ListingParser(html)
        res = parser.parse_html()
        listing = Listing(res)
        listings.append(listing)

    print(len(listings))

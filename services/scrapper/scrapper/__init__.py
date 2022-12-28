"A simple webscrapping module"

import re
import asyncio

from typing import Union
from flask import Flask, jsonify, Response

from bs4 import BeautifulSoup

from .utils import get_pages_contents, parse_html
from .models import Listing, ListingParser

app = Flask(__name__)

# app config
app.config['SECRET'] = 'random'
PAGES = 10

@app.get('/listings')
def listings() -> Union[tuple[list[dict], int], tuple[Response, int]]:
    "Return list of listing from one page"
    
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
        listings.append(listing.to_json())

    return jsonify(listings), 200

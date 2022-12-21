"A simple webscrapping module"

import re 

from typing import Union
from flask import Flask

from bs4 import BeautifulSoup

from utils import get_page_content, parse_html
from models import Listing, LISTING, LISTINGS, MAIN_PAGE

app = Flask(__name__)

# app config
app.config['SECRET'] = 'random'

@app.post('/scrap')
def scrap() -> Union[tuple[list[dict], int], tuple[str, int]]:
    "Return list of listing from one page"
    
    listings = []
    url = 'https://www.avito.ma/fr/rabat/appartements-%C3%A0_vendre'
    page_content = get_page_content(url)
    soup = BeautifulSoup(page_content, 'lxml')
    cards = soup.find_all(*LISTINGS)
    for card in cards:
        main_page_data = parse_html(str(card), MAIN_PAGE)
        listing_page = get_page_content(main_page_data['url'])
        listing_page_data = parse_html(listing_page, LISTING)
        listing = Listing(**main_page_data | listing_page_data)
        listings.append(listing)
    return listings, 200


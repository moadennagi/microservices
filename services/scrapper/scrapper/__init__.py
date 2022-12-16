"A simple webscrapping module"

from typing import Union
from flask import Flask

from .utils import PageParser
from .models import main_page_config, Listing, get_listings_from_page

app = Flask(__name__)

# app config
app.config['SECRET'] = 'random'

@app.post('/scrap')
def scrap() -> Union[tuple[list[dict], int], tuple[str, int]]:
    "Return list of listing from one page"
    listings = []
    url = 'https://www.avito.ma/fr/rabat/appartements-%C3%A0_vendre'
    parser = PageParser(config=main_page_config)

    data = get_listings_from_page(parser, url)
    for listing_data in data:
        listing = Listing(**listing_data)
        listing.set_details()
        listings.append(listing)
    return listings, 200

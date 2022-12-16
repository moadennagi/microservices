"""This module defines classes used to scrap Avito.ma
"""
import re
import datetime

from typing import Union, Any
from bs4 import BeautifulSoup
from dataclasses import dataclass, field

from .utils import PageParser

listings = ('div', {'data-testid': re.compile('adListCard.')})
main_page_config = {
    'title': '//a/div[2]/div[1]/h3/span/text()',
    'price_str': '//a/div[2]/div[1]/div/span/div/span[1]/text()',
    'location': '//a/div[2]/div[2]/div[2]/div[2]/span/text()',
    'category': '//a/div[2]/div[2]/p/text()',
    'url': '//a',
    'image': '//a/div[1]/div/img',
}
listing_config = {
    'description': '//body/div/div/main/div/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[4]/p/text()',
    'surface': '//body/div/div/main/div/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[3]/div[2]/ol/li[4]/span[2]/text()',
    'phone_number': '/html/body/div/div/main/div/div[2]/div/div/div/div/a/span'
}
listing_wr_attributes = ['title', 'location', 'url', 'price',
                         'description', 'surface', 'category', 'floor', 'sector']

@dataclass
class Listing:
    title: str
    location: str
    category: str
    url: str
    sector: str = ""
    surface: int = 0
    floor: int = 0
    description: str = ''
    price_str: str = ""
    price: int = 0
    phone_number: str = ""

    def __post_init__(self) -> None:
        """
        """
        price = self.price_str
        if price and ',' in price:
            price = price.replace(',', '')
            self.price = int(price)

    def __repr__(self) -> str:
        kws = [f"{key}={value!r}" for key, value in self.__dict__.items() if key in listing_wr_attributes]
        return "{}({})".format(type(self).__name__, ", ".join(kws))

    def set_details(self) -> dict:
        """
        """
        parser = PageParser(config=listing_config)
        html = parser.get_page_content(self.url)
        soup = BeautifulSoup(html, 'lxml')
        res = parser.parse_html_using_config(soup)
        for k in res:
            if hasattr(self, k):
                setattr(self, k, res[k])
        return res


def get_listings_from_page(parser: PageParser, url: str) -> list[dict]:
    """
        Get listing from home page
    """
    results = []
    content = parser.get_page_content(url)
    soup = BeautifulSoup(content, 'lxml')
    cards = soup.find_all('div', attrs={'data-testid': re.compile('adListCard.')})
    
    for card in cards:
        res = parser.parse_html_using_config(card)
        results.append(res)

    return results

if __name__ == '__main__':
    listings = []
    url = 'https://www.avito.ma/fr/rabat/appartements-%C3%A0_vendre'
    parser = PageParser(config=main_page_config)

    data = get_listings_from_page(parser, url)
    for listing_data in data[:1]:
        listing = Listing(**listing_data)
        listing.set_details()
        print(listing)
"""This module defines classes used to scrap Avito.ma
"""

import re
import datetime
import asyncio
from typing import Union

from bs4 import BeautifulSoup

from lxml import etree

from dataclasses import dataclass, field

from utils import get_page_content, get_pages_contents, parse_html


LISTING: dict = {
    'title': '//body/div/div/main/div/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/h1',
    'price': '//body/div/div/main/div/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/p',
    'description': '//body/div/div/main/div/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[4]/p',
    'surface': '//body/div/div/main/div/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[3]/div[2]/ol/li[6]/span[2]',
    'phone_number': '/html/body/div/div/main/div/div[2]/div/div/div/div/a/span',
    'details': '/html/body/div/div/main/div/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[3]/div[2]/ol',
    'equipments': '/html/body/div/div/main/div/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[5]/div'
}

class Listing:
    """Class representing a Listing
    """

    REPR = ['title', 'location', 'url', 'price', 'surface', 'category',]

    def __init__(self, data: dict) -> None:
        self.details = data
        self.title = data.get('title')
        self.location = data.get('location')
        price = data.get('price')
        if price:
            self.price = self.clean_price(price)

        surface = self.details.get('surface_habitable')
        if surface:
            self.surface = int(surface)

    def clean_price(self, x: str) -> Union[int, None]:
        price = None
        try:
            x = x.encode("ascii", "ignore").decode().strip()
            price = x.replace('DH', '')
            price = int(price)
        except ValueError as e:
            print(e)
        return price

    def __repr__(self) -> str:
        kws = [f"{key}={value!r}" for key, value in self.__dict__.items() if key in self.REPR]
        return "{}({})".format(type(self).__name__, ", ".join(kws))


class ListingParser:

    """Class used to parse html page
    """

    skip = ['description', 'details', 'surface']

    def __init__(self, html: str, config: dict = LISTING) -> None:
        dom = etree.HTML(html)
        self.dom = dom
        self.config = config

    def _parse_description(self) -> str:
        description = ""
        node = self.dom.xpath(self.config['description'])
        if node:
            node = node[0]
            description = ''.join(node.itertext())
        return description

    def _parse_list(self, key: str, tag: str) -> dict:
        """
            Parse nested html elements
        """
        details = {}
        labels = []
        node = self.dom.xpath(self.config[key])
        if node:
            node = node[0]
            for item in node.iter(tag):
                children = item.getchildren()
                if children:
                    label, value = children
                    k = label.text.strip().lower().replace(' ', '_')
                    details[k] = value.text
                else:
                    labels.append(item.text)
        if labels:
            details[key] = labels
        return details

    def _parse_attrs(self) -> dict:
        res = {}
        for key, value in self.config.items():
            if key not in self.skip:
                node = self.dom.xpath(value)
                if node:
                    node = node[0]
                    if key == 'url':
                        value = node.attrib['href']
                    else:
                        value = node.text
                    if key == 'price':
                        breakpoint()
                    res[key] = value
        return res

    def parse_html(self) -> dict:
        res = {}
        description = self._parse_description()
        details = self._parse_list('details', 'li')
        equipments = self._parse_list('equipments', 'span')
        attrs = self._parse_attrs()
        res['description'] = description
        res |= attrs | details | equipments
        return res


if __name__ == '__main__':

    listings = []
    tag = {'url': '//a'}

    urls = [f'https://www.avito.ma/fr/maroc/appartements-%C3%A0_vendre?o={i}' for i in range(1)]
    res = asyncio.run(get_pages_contents(urls))

    urls = []
    for html in res:
        # get the cards
        soup = BeautifulSoup(html, 'lxml')
        cards = soup.find_all('div', {'data-testid': re.compile('adListCard.')})
        for card in cards:
            html = str(card)
            data = parse_html(html, tag)
            urls.append(data.get('url'))

    res = asyncio.run(get_pages_contents(urls))
    for html in res:
        parser = ListingParser(html)
        res = parser.parse_html()
        listing = Listing(res)
        listings.append(listing)

    for listing in listings:
        print(listing.details)

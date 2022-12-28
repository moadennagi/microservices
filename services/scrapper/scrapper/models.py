"""This module defines classes used to scrap Avito.ma
"""

import re
import datetime
import asyncio
from typing import Union

from bs4 import BeautifulSoup

from lxml import etree

from dataclasses import dataclass, field, asdict


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

    def clean_price(self, x: str) -> int:
        price = 0
        try:
            x = x.encode("ascii", "ignore").decode().strip()
            price_str = x.replace('DH', '')
            price = int(price_str)
        except ValueError as e:
            print(e)
        return price

    def __repr__(self) -> str:
        kws = [f"{key}={value!r}" for key, value in self.__dict__.items() if key in self.REPR]
        return "{}({})".format(type(self).__name__, ", ".join(kws))

    def to_json(self) -> dict:
        return self.__dict__



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
    pass

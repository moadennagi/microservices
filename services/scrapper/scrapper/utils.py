"""Utils to scrap Avito
"""
import re
import json

from typing import Union
from dataclasses import dataclass, field

from lxml import etree
from bs4 import BeautifulSoup
from requests_cache import CachedSession


# requests config
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"
}

# requests cache
session = CachedSession('cache', backend='sqlite')


class PageParser:

    def __init__(self, config: dict, headers: dict = headers) -> None:
        self.config = config
        self.headers = headers

    def parse_html_using_config(self, html: BeautifulSoup, skip : list[str] = []) -> dict:
        """
            Parses the html content using keys in config.
            the dictionaries will have the same keys as the config except for listings.
            if url is in the key description get the href
        """
        data = {}
        # handle case when html is empty
        dom = etree.HTML(str(html))
        for k in self.config.keys():
            if k in skip:
                continue
            value = dom.xpath(self.config[k])
            if not value: 
                continue
            data[k] = value[0]
            if 'url' in k:
                value = value[0].attrib['href']
                data[k] = value
        return data

    def get_page_content(self, url: str) -> str:
        """
            Return page content from given url
        """
        content = ""
        with session:
            response = session.get(url, headers=self.headers, verify=False)
        if response.status_code == 200:
            content = response.text

        return content
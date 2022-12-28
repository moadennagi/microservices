"""Utils to scrap Avito
"""

import asyncio
import aiohttp

from aiohttp_client_cache import CachedSession, SQLiteBackend

from lxml import etree

# requests config
HEADERS : dict = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"
}

# TODO: move to configuration
cache = SQLiteBackend(
    cache_name='aiohttp-requests.sqlite'
)

def parse_html(html: str, config: dict, skip : list[str] = []) -> dict:
    """
        Parses the html content using keys in config.
        the dictionaries will have the same keys as the config except for listings.
        if url is in the key description get the href
    """
    data = {}
    # handle case when html is empty
    dom = etree.HTML(html)
    for k in config.keys():
        if k in skip:
            continue
        value = dom.xpath(config[k])
        if not value: 
            continue
        if 'url' in k:
            value = value[0].attrib['href']
            data[k] = value
        else:
            data[k] = value[0]
    return data

async def get_page_content(url: str) -> str:
    "Get html content of the given url"
    content = ""
    async with CachedSession(cache=cache) as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
            return content

async def get_pages_contents(urls: list[str]) -> list[str]:
    ""
    reqs = []
    for url in urls:
        reqs.append(get_page_content(url))
    results = await asyncio.gather(*reqs)
    return results

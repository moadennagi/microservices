""
import re
import requests
import time
import asyncio
import aiohttp

from typing import Callable

PAGES: int = 100


def time_it(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        print(time.time()-start)
    return wrapper

async def get_content(session: requests.Session, url: str) -> requests.Response:
    response = session.get(url=url)
    return response

async def get_all(session: requests.Session, urls: list[str]):
    reqs = []
    for url in urls:
        reqs.append(get_content(session, url))
    results = await asyncio.gather(*reqs)
    return results

@time_it
def main_sync():
    results = []
    for i in range(PAGES):
        url = f'http://books.toscrape.com/catalogue/page-{i}.html'
        response = requests.get(url=url, verify=False)
        results.append(response)
    print(results)
    return results

async def main():
    start = time.time()
    urls = [f'http://books.toscrape.com/catalogue/page-{i}.html' for i in range(PAGES)]
    with requests.Session() as session:
        results = await get_all(session, urls)
    print(results)
    print(time.time()-start)

async def get_content_aiohttp(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response

async def main_aiohttp():
    reqs = []
    start = time.time()
    urls = [f'http://books.toscrape.com/catalogue/page-{i}.html' for i in range(PAGES)]
    for url in urls:
        reqs.append(get_content_aiohttp(url))
    results = await asyncio.gather(*reqs)

    reqs = []
    urls = ['http://books.toscrape.com/catalogue/category/books/travel_2/index.html' for _ in range(10)]
    for res in results:
        for url in urls:
            reqs.append(get_content_aiohttp(url))
    results = await asyncio.gather(*reqs)

    for res in results:
        print(res.text)
    print(time.time()-start)

if __name__ == '__main__':
    # main_sync()

    # asyncio.run(main())
    asyncio.run(main_aiohttp())
""
import re

LISTINGS : tuple = ('div', {'data-testid': re.compile('adListCard.')})
MAIN_PAGE: dict = {
    'title': '//a/div[2]/div[1]/h3/span/text()',
    'price_str': '//a/div[2]/div[1]/div/span/div/span[1]/text()',
    'location': '//a/div[2]/div[2]/div[2]/div[2]/span/text()',
    'category': '//a/div[2]/div[2]/p/text()',
    'url': '//a',
    'image': '//a/div[1]/div/img',
}
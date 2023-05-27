from bs4 import BeautifulSoup
from scrapers.base_scrapers import ArcPublishingScraper
import requests


class CincoDiasScraper(ArcPublishingScraper):

    def get_headlines(self, category, **kwargs):
        limit = kwargs.get('limit', 1)
        offset = kwargs.get('offset', 0)
        parms = {
            'categoryId': category.get('categoryId'),
            'limit': limit,
            'offset': offset
        }

        url = category.get('url')
        res = self.query(url, **parms)
        return res
import json
import pandas as pd

from scrapers.abc.scraper import ABCScraper
from scrapers.lanacion.scraper import LaNacionScraper
from database.xata_api import XataAPI


class Scraper:
    """
    Scraper class to be used by the crawler jobs.
        :param site: Can be only 'abc' for the moment.
    """

    def __new__(cls, site, *args, **kwargs):
        if site == 'abc':
            inst = super().__new__(BaseABCScraper)
        elif site == 'lanacion':
            inst = super().__new__(BaseLaNacionScraper)
        else:
            raise ValueError(f"Unknown site: {site}")
        return inst

    def set_parameters(self, parameters, query_args={}):
        categories = parameters.pop('categories')
        endpoints = parameters.pop('endpoints')
        self._categories = [json.loads(cat.replace("'", '"')) for cat in categories]
        r = dict()
        for endpoint in endpoints:
            key, value = endpoint.split('=')
            value = json.loads(value)
            r.update({key: value})
        parameters.update(dict(endpoints=r))
        self._parameters.update(parameters)
        self._query.update(query_args)

    def load_parameters(self):
        params = self._db.query('news_publisher', filter={'publisher_name': 'abc'})[0]
        self.set_parameters(params)
        return params

    def save_metadata(self):
        params, c = self._db.get_or_create('news_publisher', {'publisher_name': self.site})

        new_params = {'publisher_name': str(self.site),
                      'website': str(self.parameters.get('website', None)),
                      'categories': [str(cat) for cat in self.categories],
                      'endpoints': [f"{key}={json.dumps(value)}" for key, value in self.endpoints.items()]
                      }

        new_params = self._db.update('news_publisher', params['id'], new_params)
        return new_params

    def save_article(self, article):
        q = article.copy()
        q.pop('id', None)
        q.pop('xata', None)
        q.pop('article_body', None)
        q.pop('title', None)
        q.pop('subtitle', None)
        current, c = self._db.get_or_create('news_article', q)
        r = self._db.update('news_article', current['id'], article)

        return r

    @property
    def endpoints(self):
        return self._parameters.get('endpoints', {})

    @property
    def categories(self):
        if not self._categories:
            self._categories = self.load_parameters()
        if not self._categories:
            try:
                self._categories = self.get_categories()
            except AttributeError:
                self._categories = []
        return self._categories

    @property
    def parameters(self):
        return self._parameters


class BaseScraper(Scraper):
    def __init__(self, *args, **kwargs):
        self._categories = None
        self._data = pd.DataFrame()
        self._query = {}
        self._parameters = {}
        self._db = XataAPI(branch=kwargs.pop('branch', 'main'))
        self.load_parameters()


class BaseABCScraper(ABCScraper, BaseScraper):
    pass


class BaseLaNacionScraper(LaNacionScraper, BaseScraper):
    pass

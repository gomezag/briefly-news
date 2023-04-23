import os
import yaml
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
            return super().__new__(BaseABCScraper, *args, **kwargs)
        elif site == 'lanacion':
            return super().__new__(BaseLaNacionScraper, *args, **kwargs)
        else:
            raise ValueError(f"Unknown site: {site}")

    def set_parameters(self, parameters, query_args={}):
        self._parameters.update(parameters)
        self._query.update(query_args)

    def load_parameters(self, file=None):
        if not file:
            file = os.path.join(os.path.dirname(__file__), 'defaults.yaml')
        with open(file, 'r') as f:
            defaults = yaml.safe_load(f).get(self.__class__.__base__.__name__, None)
            if not defaults:
                raise ValueError('No base url defined for this site.')
            self.set_parameters(defaults)

    def get_daily_report(self):
        """
        A daily report generator.
        :return: A pandas DataFrame with articles as plain rows of consecutive text,
        in the way that is going to be presented to the Embeddings API.
        """
        pass

    def query(self, *args, **kwargs):
        """
        Basic query method.
        :return: A dictionary with the result of a query for the given scraper.
        """
        return {}

    def get_categories(self, *args, **kwargs):
        raise ValueError(f'This method is not defined for {self.__class__}')

    def get_headlines(self, *args, **kwargs):
        raise ValueError(f'This method is not defined for {self.__class__}')

    def load_headlines(self, *args, **kwargs):
        try:
            categories = pd.read_csv(f'data/{self.site}/headlines.csv')
            return categories.to_dict()
        except FileNotFoundError:
            return None

    def load_categories(self, *args, **kwargs):
        try:
            categories = pd.read_csv(f'data/{self.site}/categories.csv')
            categories = [{'id': cat[1].values[1], 'uri': cat[1].values[2]} for cat in categories.iterrows()]
            return categories
        except FileNotFoundError:
            return None

    @property
    def endpoints(self):
        return self._parameters.get('endpoints', {})

    @property
    def categories(self):
        if not self._categories:
            self._categories = self.load_categories()
        if not self._categories:
            self._categories = self.get_categories()
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
        self.load_parameters()
        self._db = XataAPI()


class BaseABCScraper(ABCScraper, BaseScraper):
    pass


class BaseLaNacionScraper(LaNacionScraper, BaseScraper):
    pass

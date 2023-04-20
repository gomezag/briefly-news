import os
import yaml
import pandas as pd

from .abc.scraper import ABCScraper
from .lanacion.scraper import LaNacionScraper


class Scraper:
    """
    Scraper class to be used by the crawler jobs.
        :param site: Can be only 'abc' for the moment.
    """

    def __init__(self, *args, **kwargs):
        self._data = pd.DataFrame()
        self._query = {}
        self._parameters = {}
        file = os.path.join(os.path.dirname(__file__), 'defaults.yaml')
        with open(file) as f:
            defaults = yaml.safe_load(f).get(self.__class__.__base__.__name__, None)
            if not defaults:
                raise ValueError('No base url defined for this site.')
            self.set_parameters(defaults)

    def __new__(cls, site, *args, **kwargs):
        if site == 'abc':
            return super().__new__(BaseABCScraper, *args, **kwargs)
        elif site == 'lanacion':
            return super().__new__(BaseLaNacionScraper, *args, **kwargs)
        else:
            raise ValueError(f"Unknown site: {site}")

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

    @property
    def endpoints(self):
        return self._parameters.get('endpoints', {})


class BaseABCScraper(ABCScraper, Scraper):
    pass


class BaseLaNacionScraper(LaNacionScraper, Scraper):
    pass

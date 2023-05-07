import json
import pandas as pd
import logging

from scrapers.abc.scraper import ABCScraper
from scrapers.lanacion.scraper import LaNacionScraper
from database.xata_api import XataAPI


class Scraper:
    """
    Scraper class to be used by the crawler jobs.
    It initializes itself as a type according to the site input. When it matches a defined scraper type, it
    initializes the BaseXScraper, which inherits the methods from the XScraper class.

    Inputs:

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

    def set_parameters(self, parameters):
        """
        Sets internal parameters according to the input dictionary.
        It will take apart the categories input and load the json data for each of the elements in the list.
        It will read the endpoints as a list of key=jsonDict elements with a path and data elements.
        Finally, it will update _parameters to the parsed dictionary.

        Inputs:

            :param parameters: a parameter dictionary.

        Output:

            :return: None
        """
        categories = parameters.pop('categories', None)
        endpoints = parameters.pop('endpoints', None)
        if categories:
            try:
                logging.info("Parsing categories...")
                self._categories = [json.loads(cat.replace("'", '"')) for cat in categories]
            except:
                logging.info("Could not parse categories. Initializing to None.")
                logging.info(categories)
        if endpoints:
            r = dict()
            for endpoint in endpoints:
                key, value = endpoint.split('=')
                value = json.loads(value)
                r.update({key: value})
            parameters.update(dict(endpoints=r))
        self._parameters.update(parameters)

    def load_parameters(self):
        """
        Get parameters from the database and update the instance.

        Output:

            :return: the parameter dictionary
        """
        params = self._db.query('news_publisher', filter={'publisher_name': self.site})[0]
        self.set_parameters(params)
        return params

    def save_metadata(self):
        """
        Save the current parameters to the database.

        Output:

            :return: parameters as they are read from the database after saving

        """
        params, c = self._db.get_or_create('news_publisher', {'publisher_name': self.site})

        new_params = {'publisher_name': str(self.site),
                      'website': str(self.parameters.get('website', None)),
                      'categories': [json.dumps(cat) for cat in self.categories],
                      'endpoints': [f"{key}={json.dumps(value)}" for key, value in self.endpoints.items()]
                      }

        new_params = self._db.update('news_publisher', params['id'], new_params)
        return new_params

    def save_article(self, article):
        """
        Save an article to the database.
        It will try to match any entry with a possibly different body or subtitle, to get_or_create a new article
        in the database with the input dictionary

        Input:

            :param article: a valid article dictionary

        Output:

            :return: response from the database server.

        """
        article.pop('xata', None)
        q = article.copy()
        q.pop('article_body', None)
        q.pop('subtitle', None)
        current, c = self._db.get_or_create('news_article', q)
        r = self._db.update('news_article', current['id'], article)

        return r

    @property
    def endpoints(self):
        return self._parameters.get('endpoints', {})

    @property
    def categories(self):
        if self._categories == [] or not self._categories:
            self.load_parameters()
        if self._categories == [] or not self._categories:
            try:
                self._categories = self.get_categories()
            except AttributeError:
                self._categories = []
        return self._categories

    @property
    def parameters(self):
        return self._parameters


class BaseScraper(Scraper):
    """
    These are common initializations that can/should be added in the BaseXScraper class.

    """
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

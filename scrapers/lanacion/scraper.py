from ..abc.scraper import ArcPublishingScraper
import pandas as pd

class LaNacionScraper(ArcPublishingScraper):

    def __init__(self, *args, **kwargs):
        self.site = 'abc'
        self._categories = None
        self._data = pd.DataFrame()
        self._query = {}
        self._parameters = {}
        self.load_parameters()

from ..abc.scraper import ABCScraper


class LaNacionScraper(ABCScraper):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
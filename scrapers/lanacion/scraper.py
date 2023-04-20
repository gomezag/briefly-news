from ..abc.scraper import ABCScraper


class LaNacionScraper(ABCScraper):
    """
    Possible query parameters:
        query = {"arc-site": "abccolor",
             "id": "/nacionales",
             "limit": "5",
             "offset": 15,
             "sort": "display_date:desc",
             "uri": "/nacionales/"}
    """

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
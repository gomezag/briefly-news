from scrapers.base_scrapers import ArcPublishingScraper


class LaNacionScraper(ArcPublishingScraper):

    def __init__(self, *args, **kwargs):
        self.site_id = 'lanacion'
        self.site = 'lanacion'
        super().__init__(*args, **kwargs)

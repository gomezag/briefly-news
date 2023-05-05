import urllib.parse as urlparse

from scrapers.base_scrapers import ArcPublishingScraper


class LaNacionScraper(ArcPublishingScraper):

    def __init__(self, *args, **kwargs):
        self.site_id = 'lanacion'
        self.site = 'lanacion'
        super().__init__(*args, **kwargs)

    def get_headlines(self, category, *args, **kwargs):
        """
        Get the latest headlines
        :param category: a dictionary with an 'id' and 'uri' field
        :param kwargs: extra arguments will be updated in the query dictionary, such as limit
        :return: a list with the results.
        """
        endpoint = self.endpoints.get('headlines', None)
        if not endpoint:
            raise ValueError(f'Headlines endpoint not defined for {self.__class__}')
        query = endpoint['data']
        query['query'].update(category)
        limit = kwargs.pop('limit', None)
        if limit:
            query['query'].update({'feedSize': limit})
        query['query'].update(**kwargs)
        url = endpoint['path']
        r = self.query(url, **query).json()
        headlines = r['content_elements']
        articles = []
        for head in headlines:
            title = head['headlines']['basic']
            # subtitle = head['subheadlines']['basic']
            # published = head['publish_date']
            # updated = head['last_updated_date']
            date = head['display_date']
            # first_publish = head['publish_date']
            url = urlparse.urljoin(self._parameters['website'], head['canonical_url'])
            try:
                authors = [c['name'] for c in head['credits']['by']]
            except KeyError:
                authors = []
            articles.append(dict(
                title=title,
                date=date,
                url=url,
                authors=authors,
                publisher=self.parameters['id'],

            ))

        return articles, r

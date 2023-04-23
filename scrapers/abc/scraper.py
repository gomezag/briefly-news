import urllib.parse as urlparse
from scrapers.base_scrapers import ArcPublishingScraper


class ABCScraper(ArcPublishingScraper):
    def __init__(self, *args, **kwargs):
        self.site = 'abc'
        self.site_id = 'abc'
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
        query['query'].update(**kwargs)
        url = endpoint['path']
        r = self.query(url, **query).json()
        headlines = r['content_elements']
        articles = []
        for head in headlines:
            title = head['headlines']['basic']
            subtitle = head['subheadlines']['basic']
            # published = head['publish_date']
            # updated = head['last_updated_date']
            date = head['display_date']
            # first_publish = head['publish_date']
            url = urlparse.urljoin(self._parameters['website'], head['website_url'])
            owner = head['owner']['id']
            source = head['source']['name']
            try:
                authors = [c['_id'] for c in head['credits']['by'] if c['type'] == 'author']
            except KeyError:
                authors = []
            id = head['_id']
            articles.append(dict(
                title=title,
                subtitle=subtitle,
                date=date,
                url=url,
                owner=owner,
                source=source,
                authors=authors,
                id=id
            ))

        return articles, r

    def get_categories(self, *args, **kwargs):
        """
        Get the categories as a dataframe with the query parameters to get the headlines.
        :param args:
        :param kwargs:
        :return:
        """
        endpoint = self.endpoints.get('categories', None)
        if not endpoint:
            raise ValueError(f'Category endpoint not defined for {self.__class__}')

        query_data = endpoint.get('data', {})
        data = self.query(endpoint['path'], **query_data).json()['children']
        r = []
        for el in data:
            try:
                url = el['site']['site_url']
                if not url.startswith('/'):
                    url = '/'+url
                if not url.endswith('/'):
                    url = url+'/'
                r.append({'id': el['_id'], 'uri': url})
            except (KeyError, AttributeError):
                pass
        return r

import json
from requests import HTTPError

from bs4 import BeautifulSoup
import urllib.parse as urlparse

from scrapers.base_scrapers import ArcPublishingScraper
import time

class ABCScraper(ArcPublishingScraper):

    def get_headlines(self, category, *args, **kwargs):
        """
        Get the latest headlines

        Inputs:

            :param category: a dictionary with an 'id' and 'uri' field
            :param kwargs: extra arguments will be updated in the query dictionary, such as limit

        Output:

            :return:
                - a list with the results.
                - the full json of the response. Useful for debug.
        """
        endpoint = self.endpoints.get('headlines', None)
        if not endpoint:
            raise ValueError(f'Headlines endpoint not defined for {self.__class__}')
        query = endpoint['data']
        query['query'].update(category)
        url = endpoint['path']
        headlines = []
        limit = kwargs.pop('limit')
        offset = kwargs.pop('offset')
        i = int(offset)
        limit = int(offset)+limit
        while i < min(limit, offset+1000):
            kwargs.update(dict(limit=str(min(100, limit-i)),
                               offset=str(i)))
            query['query'].update(**kwargs)
            r = self.query(url, **query).json()
            arts = r['content_elements']
            if len(arts):
                headlines.extend(arts)
                i += 100
            else:
                break

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
            source = head.get('source', {}).get('name', self.site)
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
                publisher=self.parameters['id'],
                article_id=id
            ))

        return articles, r

    def get_categories(self, *args, **kwargs):
        """
        Get the categories as a dataframe with the query parameters to get the headlines.

        Inputs:

            :param args:
            :param kwargs:

        Output:

            :return: a list of categories ready to be added to the parameters of the scraper.

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
                    url = '/' + url
                if not url.endswith('/'):
                    url = url + '/'
                r.append({'id': el['_id'], 'uri': url})
            except (KeyError, AttributeError):
                pass
        return r

    def get_article_body(self, article):
        """
        Get a full article by parsing the html response

        Inputs:

            :param article: an article dictionary with a valid url.

        Output:

            :return:
                - article: the updated article dictionary
                - article_data: the full dictionary data found.
        """
        try:
            r = self.query(article['url'])
            soup = BeautifulSoup(r.text, 'html.parser')
            errors = []
            for script in soup.find_all('script'):
                text = script.text
                if text.find('"articleBody"'):
                    try:
                        article_data = json.loads(text)
                        article['article_body'] = article_data['articleBody']
                        return article, article_data
                    except Exception as e:
                        errors.append(e)

            return article, errors
        except HTTPError as e:
            return article, e

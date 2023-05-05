import urllib.parse as urlparse
import requests
import json
from bs4 import BeautifulSoup

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

    def get_article_body(self, article):
        res = requests.get(article['url'])
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for script in soup.findAll('script'):
                article = self._extract_article(script.text, 'Fusion.globalContent=')
                if article:
                    body = article.get('description', {}).get('basic', None)
                    if body:
                        return body, article
        else:
            return None

    @staticmethod
    def _extract_article(text, keyword):
        # Find the index of the start of the text you want to extract
        start = text.find(keyword)
        if start:
            if start > 0:
                start = start + len(keyword)
                # Find the index of the end of the text you want to extract
                end = start + 1
                count = 1
                while count != 0 and end < len(text):
                    if text[end] == '{':
                        count += 1
                    elif text[end] == '}':
                        count -= 1
                    end += 1

                # Extract the text between the start and end indices
                extracted_text = text[start:end]
                return json.loads(extracted_text)
        return None

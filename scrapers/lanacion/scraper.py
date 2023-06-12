import urllib.parse as urlparse
import json
from bs4 import BeautifulSoup
from requests import HTTPError

from scrapers.base_scrapers import ArcPublishingScraper


class LaNacionScraper(ArcPublishingScraper):

    def get_headlines(self, category, *args, **kwargs):
        """
        Get the latest headlines
        :param category: a dictionary with an 'id' and 'uri' field
        :param kwargs: extra arguments will be updated in the query dictionary, such as limit
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
            kwargs.update(dict(feedSize=str(min(100, limit-i)),
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
        """
        Get a full article by parsing the html response
        :param article: an article dictionary with a valid url.
        :return:
            - article: the updated article dictionary
            - full_article: the full dictionary data found.
        """
        try:
            res = self.query(article['url'])
            soup = BeautifulSoup(res.text, 'html.parser')
            for script in soup.findAll('script'):
                full_article = self._extract_article(script.text, 'Fusion.globalContent=')
                if full_article:
                    subtitle = full_article.get('description', {}).get('basic', '')
                    body_list = full_article.get('content_elements', [])
                    body = ''
                    if len(body_list) > 0:
                        for el in body_list:
                            if el.get('type', '') == 'text':
                                text = el.get('content', '')
                                if text != '':
                                    body += ' '+str(text)
                    if body != '':
                        article['article_body'] = body
                    if subtitle != '':
                        article['subtitle'] = subtitle
                    return article, full_article
        except HTTPError as e:
            return article, e

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

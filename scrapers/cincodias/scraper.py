from bs4 import BeautifulSoup
from scrapers.base_scrapers import ArcPublishingScraper
import requests
import locale
import datetime


class CincoDiasScraper(ArcPublishingScraper):

    def get_headlines(self, category, **kwargs):
        limit = kwargs.get('limit', 1)
        offset = kwargs.get('offset', 0)
        parms = {
            'categoryId': category.get('categoryId'),
            'limit': limit+1,
            'offset': offset
        }

        res = self.query('api/category/timeline', **parms)
        soup = BeautifulSoup(res.text, 'html.parser')
        farticles = soup.find_all('article')[:-1]

        articles = []
        for article in farticles:
            url = article.find_all('h2')[0].find_all('a')[0].attrs['href']
            title = article.find_all('h2')[0].text
            extra_title = article.find_all('h3')
            if extra_title:
                title += extra_title[0].text
            try:
                subtitle = article.find_all('p')[0].text
            except IndexError:
                subtitle = ''
            articles.append(dict(url=url,
                                 title=title,
                                 subtitle=subtitle,
                                 publisher=self.parameters['id'],
                                 authors=['5Dias']))
        return articles, res

    def get_article_body(self, article):
        locale.setlocale(locale.LC_TIME, 'es_ES')
        url = article.get('url')
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        intro = soup.find_all('div', {'class': 'v-article-intro'})[0]
        body = soup.find_all('div', {'class': 'v-article-body'})[0]
        article_body = " \n ".join([str(p.text) for p in body.find_all('p')])
        date = " ".join(intro.find_all('h3')[0].text.split())
        date = datetime.datetime.strptime(date, '%d %B de %Y %H:%M').strftime('%Y-%m-%dT%H:%M:%SZ')
        article.update(dict(
            article_body=article_body,
            date=date
        ))

        return article, soup

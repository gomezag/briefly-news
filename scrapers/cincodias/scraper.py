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

        # Work around for limitation of 10 articles imposed by site.
        retry = True
        while len(farticles) < limit and retry:
            try:
                parms.update({'offset': len(farticles)})
                res = self.query('api/category/timeline', **parms)
                soup = BeautifulSoup(res.text, 'html.parser')
                more_articles = soup.find_all('article')[:-1]
                farticles.extend(more_articles)
                if not more_articles:
                    retry = False
            except Exception:
                retry = False

        # Get article data from soups
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
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        url = article.get('url')
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        intro = soup.find_all('div', {'class': 'v-article-intro'})[0]
        body = soup.find_all('div', {'class': 'v-article-body'})[0]
        article_body = " \n ".join([str(p.text) for p in body.find_all('p')])
        info = intro.find_all('h3')
        date = " ".join(info[-1].text.split())
        date = datetime.datetime.strptime(date, '%d %B de %Y %H:%M').strftime('%Y-%m-%dT%H:%M:%SZ')
        authors = []
        if len(info) > 1:
            authors.extend([" ".join(intro.find_all('h3')[0].text.split()).split('Por ')[1]])
        authors.extend(article.get('authors', []))
        article.update(dict(
            article_body=article_body,
            date=date,
            authors=authors
        ))

        return article, soup

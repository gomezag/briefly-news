from scrapers.base_scrapers import HTMLScraper
from bs4 import BeautifulSoup
import json
import datetime


class UltimaHoraScraper(HTMLScraper):

    def __init__(self, *args, **kwargs):
        self.site_id = 'ultimahora'
        self.site = 'ultimahora'
        super().__init__(*args, **kwargs)

    def get_headlines(self, category, *args, **kwargs):
        limit = kwargs.get('limit', 1)
        endpoint = category.get('url', '')
        articles = []
        i = 0
        while len(articles) < limit:
            if i > 0:
                url = endpoint+'/'+str(i)
            else:
                url = endpoint
            res = self.query(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            articles.extend([{'url': list(set([a.attrs['href'] for a in article.find_all('a')]))[0]}
                for article in soup.find_all('article')
            ])
            i += 1
        articles = [{key: value} for key, value in list(set([tuple(a.items())[0] for a in articles]))]
        return articles, res

    def get_article_body(self, article):
        url = article.get('url', None)
        if not url:
            raise ValueError('URL of article can''t be empty.')
        res = self.query(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        data = json.loads(str(soup.find_all('script')[0].text))[0]
        title = data.get('headline', '')
        subtitle = data.get('description', '')
        body = data.get('articleBody', '')
        publisher = self.parameters['id']
        date = data.get('datePublished', datetime.datetime.now())
        authors = [a['name'] for a in data.get('author', [])]
        article.update({
            'title': title,
            'subtitle': subtitle,
            'article_body': body,
            'authors': authors,
            'date': date,
            'publisher': publisher,
        })
        return article, data

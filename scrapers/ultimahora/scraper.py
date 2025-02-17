from scrapers.base_scrapers import HTMLScraper
from bs4 import BeautifulSoup
import json
import datetime


class UltimaHoraScraper(HTMLScraper):

    def get_headlines(self, category, *args, **kwargs):
        limit = kwargs.get('limit', 1)
        endpoint = category.get('url', '')
        articles = []
        i = 1
        while len(articles) < limit:
            if i > 1:
                url = endpoint+'?p='+str(i)
            else:
                url = endpoint
            res = self.query(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            extras = []
            for article in soup.find_all('div', {'class': 'PageList-items-item'}):
                links = article.find_all('a')
                if links:
                    url = links[0].attrs['href']
                    if self.parameters['website'] in url:
                        extras.append({'url': url})
            if len(extras):
                articles.extend(extras)
                i += 1
            else:
                break

        articles = [{key: value} for key, value in list(set([tuple(a.items())[0] for a in articles]))]
        articles = articles[:limit]
        return articles, res

    def get_article_body(self, article):
        url = article.get('url', None)
        if not url:
            raise ValueError('URL of article can''t be empty.')
        res = self.query(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        data = json.loads(str(soup.find_all('script')[0].text))
        title = data.get('headline', '')
        subtitle = data.get('description', '')
        publisher = self.parameters['id']
        date = data.get('dateModified', '')
        authors = [a['name'] for a in data.get('author', [])]
        bodies = []
        for el in soup.find_all('div', {'class': 'Page-articleBody'}):
            bodies.extend(el.find_all('p'))
        body = ' '.join([b.text for b in bodies])
        # body = data.get('articleBody', '')
        article.update({
            'title': title,
            'subtitle': subtitle,
            'article_body': body,
            'authors': authors,
            'date': date,
            'publisher': publisher,
        })
        return article, data

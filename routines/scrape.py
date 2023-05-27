import sys
import logging

from scrapers import Scraper
from llm.utils import get_related_people


def scrape_headlines(scraper, limit=15):
    for category in scraper.categories:
        headlines, r = scraper.get_headlines(category, limit=limit)
        logging.info(f"Found {len(headlines)} articles for category {category}.")
        N = len(headlines)
        skips = 0
        for i, article in enumerate(headlines):
            try:
                filter = {'url': article['url']}
                if article.get('title', None):
                    filter.update({'title': article['title']})
                qarticle = scraper._db.query('news_article', filter=filter)['records']
                if len(qarticle) > 0:
                    if qarticle[0].get('article_body', None):
                        # If there is an article with that url and an article body, skip the article.
                        skips += 1
                        continue
                logging.info(f"Scraping article {i} of {N}")
                article, r = scraper.get_article_body(article)
                counts, articles = get_related_people([article], 'PER')
                article = articles[0]
                article['POIs'] = list(set(article['POIs']))
                article = scraper.save_article(article)
            except Exception as e:
                logging.info(f"Error in article {i} of {N}.")
                logging.info(f"{article}")
                logging.info(repr(e))
        logging.info(f"Skipped {skips}/{N} articles for category {category}.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.root.setLevel(logging.INFO)

    try:
        branch = sys.argv[1]
    except IndexError:
        branch = 'main'

    try:
        limit = int(sys.argv[2])
    except IndexError:
        limit = 15

    for site in ['abc', 'lanacion', 'ultimahora']:
        try:
            scraper = Scraper(site, branch=branch)
            scrape_headlines(scraper, limit=limit)
        except Exception as e:
            print(e)

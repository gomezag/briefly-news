import sys
import logging

from scrapers import Scraper
from llm.utils import get_related_people

from threading import Thread


class ScrapeThread(Thread):
    def __init__(self, scraper, category, limit, *args, **kwargs):
        self.scraper = scraper
        self.category = category
        super(ScrapeThread, self).__init__(*args, **kwargs)

    def run(self):
        category = self.category
        scraper = self.scraper

        logging.info('Starting thread for category '+str(category)+' on site '+scraper.site)
        try:
            logging.info(f"Getting {limit} headlines for category {str(category)}")
            headlines, r = scraper.get_headlines(category, limit=limit, offset=0)
        except Exception as e:
            logging.error(f"Error in category {category}.")
            logging.error(repr(e))
            return

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
                logging.info(f"Scraping article {i} of {N} on {scraper.site} and category {category}")
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


def scrape_headlines(scraper, limit=15):
    threads = []
    for category in scraper.categories:
        threads.append(ScrapeThread(scraper, category, limit))

    for t in threads:
        t.daemon = True
        t.start()

    while(any([t.is_alive() for t in threads])):
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.root.setLevel(logging.INFO)

    branch = sys.argv[1]
    limit = int(sys.argv[2])
    sites = sys.argv[3].split(',')
    for site in sites:
        try:
            scraper = Scraper(site, branch=branch)
            scrape_headlines(scraper, limit=limit)
        except Exception as e:
            print(e)

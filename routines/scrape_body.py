import sys
import logging
import time

from database.xata_api import XataAPI
from scrapers import Scraper

logging.basicConfig(level=logging.INFO)
logging.root.setLevel(logging.INFO)

branch = sys.argv[1]

limit = sys.argv[2]

db = XataAPI(branch=branch)
scrapers = dict()
for site in ['abc', ]:
    scraper = Scraper(site, branch=branch)
    scrapers[scraper.parameters['id']] = scraper
logging.info(f'Scraping up to {limit} articles bodies on branch {branch}.')
articles = db.query('news_article', filter={'$notExists': 'article_body'}, page={'size': int(limit)})
n = len(articles)
logging.info(f'Found {n} articles.')
for i, article in enumerate(articles):
    if i % 5 == 0:
        logging.info(f"Fetching {i}/{n}")
    time.sleep(0.5)
    try:
        article['publisher'] = article['publisher']['id']
        scraper = scrapers[article['publisher']]
        body, r = scraper.get_article_body(article)
        article['article_body'] = body
        scraper.save_article(article)
    except Exception as e:
        time.sleep(2)
        logging.info(f"On {i} got {repr(e)}")
        pass

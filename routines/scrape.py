import sys
import logging

from scrapers import Scraper

logging.basicConfig(level=logging.INFO)
logging.root.setLevel(logging.INFO)


def scrape_headlines(scraper, limit=15):
    for category in scraper.categories:
        headlines, r = scraper.get_headlines(category, limit=limit)
        logging.info(f"Found {len(headlines)} articles for category {category}.")
        for i, article in enumerate(headlines):
            try:
                if i % 3 == 0:
                     logging.info(f"Scraping {i} articles...")
                body, r = scraper.get_article_body(article)
                article['article_body'] = body
                scraper.save_article(article)
            except Exception as e:
                logging.info(f"Error in article {article['url']}.")
                logging.info(repr(e))


try:
    branch = sys.argv[1]
except IndexError:
    branch = 'main'

try:
    limit = sys.argv[2]
except IndexError:
    limit = 15


for site in ['abc', ]:
    try:
        scraper = Scraper(site, branch=branch)
        scrape_headlines(scraper, limit=limit)
    except Exception as e:
        print(e)

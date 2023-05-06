import sys
import logging

from scrapers import Scraper

logging.basicConfig(level=logging.INFO)
logging.root.setLevel(logging.INFO)


def scrape_headlines(scraper, limit=15):
    for category in scraper.categories:
        headlines, r = scraper.get_headlines(category, limit=limit)
        logging.info(f"Found {len(headlines)} articles for category {category}.")
        N = len(headlines)
        skips = 0
        for i, article in enumerate(headlines):
            try:
                qarticle = scraper._db.query('news_article', filter={'url':article['url']})
                if len(qarticle)>0:
                    if qarticle[0]['article_body']:
                        skip += 1
                        continue
                logging.info(f"Scraping article {i} of {N}")
                body, r = scraper.get_article_body(article)
                article['article_body'] = body
                scraper.save_article(article)
            except Exception as e:
                logging.info(f"Error in article {i} of {N}.")
                logging.info(f"{article}")
                logging.info(repr(e))
        logging.info(f"Skipped {skips}/{N} articles.")

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

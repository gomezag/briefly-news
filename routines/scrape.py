import sys

from scrapers import Scraper


def scrape_headlines(scraper, limit=15):
    for category in scraper.categories:
        headlines, r = scraper.get_headlines(category, limit=limit)
        for article in headlines:
            scraper.save_article(article)


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

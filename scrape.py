from scrapers import Scraper


def scrape_headlines(scraper):
    for category in scraper.categories:
        headlines, r = scraper.get_headlines(category, limit=15)
        for article in headlines:
            scraper.save_article(article)


for site in ['abc', ]:
    try:
        scraper = Scraper(site=site)
        scrape_headlines(scraper)
    except Exception as e:
        print(e)

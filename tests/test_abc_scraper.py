from scrapers.scraper import Scraper
import pytest


@pytest.mark.parametrize("site", ["abc", ])
def test_scraper(site):
    scraper = Scraper(site=site)
    r = scraper.query()

    assert type(r) == dict

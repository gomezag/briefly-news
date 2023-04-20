from scrapers.scraper import Scraper
import pytest


@pytest.mark.parametrize("site", ["abc", "lanacion"])
def test_scraper(site):
    scraper = Scraper(site=site)
    r = scraper.query_defaults()

    assert type(r) == dict or all([type(e) == dict for e in r])

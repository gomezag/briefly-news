
import pytest
from scrapers import Scraper
@pytest.fixture
def scraper(site):
    yield Scraper(site=site)

@pytest.fixture
def scrape():
    return pytest.mark.scrape
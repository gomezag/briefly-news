
import pytest
from scrapers import Scraper
@pytest.fixture
def scraper(site):
    yield Scraper(site, branch='dev')

@pytest.fixture
def scrape():
    return pytest.mark.scrape
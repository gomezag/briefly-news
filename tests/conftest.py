
import pytest

from scrapers import Scraper
from database.xata_api import XataAPI


@pytest.fixture
def xata_api():
    return XataAPI(branch='dev')


@pytest.fixture
def scraper(site):
    yield Scraper(site, branch='dev')


@pytest.fixture
def scrape():
    return pytest.mark.scrape

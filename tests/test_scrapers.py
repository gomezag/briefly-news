from scrapers.scraper import Scraper
import pytest


@pytest.mark.parametrize("site", ["abc", "lanacion"])
def test_scraper(site):
    scraper = Scraper(site=site)
    endpoint = scraper.endpoints.get('headlines', None)
    if not endpoint:
        pytest.skip('No headlines endpoint defined for this scraper')
    r = scraper.query(endpoint['path'], **endpoint['data'])

    assert type(r) == dict


@pytest.mark.parametrize("site", ["abc", "lanacion"])
def test_categories(site):
    scraper = Scraper(site=site)
    try:
        r = scraper.get_categories()
        assert type(r) == list
        assert len(r) > 0
        assert type(r[0]) == dict

    except ValueError:
        pytest.skip(f'No categories endpoint defined for {site} scraper.')

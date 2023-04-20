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


@pytest.mark.parametrize("site", ["abc", ])
def test_categories(site):
    scraper = Scraper(site=site)
    # Only test one
    data, r = scraper.get_headlines(scraper.categories[15], limit=1)

    assert len(data) == 1
    assert r.get('type') == 'results'
    assert type(data[0]['headlines']['basic'] == str)

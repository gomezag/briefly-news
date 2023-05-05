import pytest
import urllib.parse as urlparse


def validate_url(url):
    try:
        r = urlparse.urlparse(url)
        return all([r.scheme, r.netloc])
    except:
        return False


@pytest.fixture
def sample_cat(site):
    # Only test one
    if site == 'abc':
        catno = 16
    elif site == 'lanacion':
        catno = 0
    return catno


@pytest.mark.parametrize("site", ["abc", "lanacion"])
def test_scraper(scraper, site):
    endpoint = scraper.endpoints.get('headlines', None)
    if not endpoint:
        pytest.skip('No headlines endpoint defined for this scraper')
    r = scraper.query(endpoint['path'], **endpoint['data']).json()
    assert type(r) == dict


@pytest.mark.parametrize("site", ["abc", "lanacion"])
def test_categories(scraper, site):
    cats = scraper.categories
    assert type(cats) == list
    assert type(cats[0]) == dict


@pytest.mark.parametrize("site", ["abc", "lanacion"])
def test_headlines(scraper, site, sample_cat):
    data, r = scraper.get_headlines(scraper.categories[sample_cat], limit=1)
    assert len(data) == 1
    story = data[0]
    assert type(story['title']) == str
    assert type(story['authors']) == list
    assert validate_url(story['url'])
    if site == 'abc':
        assert r.get('type') == 'results'
        assert type(story['source']) == str


@pytest.mark.parametrize("site", ["abc", "lanacion"])
def test_article(scraper, site, xata_api, sample_cat):

    arts, r = scraper.get_headlines(scraper.categories[sample_cat], limit=1)
    art = arts[0]
    body, r = scraper.get_article_body(art)
    assert type(body) == str

    art['article_body'] = body

    saved_article = scraper.save_article(art)
    try:
        article = xata_api.query('news_article', filter=art)[0]
        assert saved_article['id'] == article['id']
    finally:
        xata_api.delete('news_article', saved_article['id'])

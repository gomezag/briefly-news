import requests


def get_articles(query):
    url = f'https://www.abc.com.py/pf/api/v3/content/fetch/sections-api?query={"{" + query + "}"}'
    r = requests.get(url)
    if r.status_code == '200':
        return r.json()
    else:
        raise requests.HTTPError(r.text)


def gen_query(**kwargs):
    query = {"arc-site": "abccolor",
             "id": "/nacionales",
             "limit": "5",
             "offset": 15,
             "sort": "display_date:desc",
             "uri": "/nacionales/"}
    query.update(**kwargs)

    return query


def query(**kwargs):
    return get_articles(gen_query(**kwargs))






import requests


def get_articles(query):
    squery = "{"
    squery += ",".join(['"'+str(key)+'":"'+str(value)+'"' for key, value in query.items()])
    squery += "}"
    url = f'https://www.abc.com.py/pf/api/v3/content/fetch/sections-api?query={squery}'
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        print(r.status_code)
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


if __name__=='__main__':
    r = query(limit=15)
    print(r)
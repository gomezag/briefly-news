import requests

DEFAULT_QUERY = {"arc-site": "abccolor",
                 "id": "/nacionales",
                 "limit": "5",
                 "offset": 15,
                 "sort": "display_date:desc",
                 "uri": "/nacionales/"}


class ABCScraper:
    """
    Possible query parameters:
        query = {"arc-site": "abccolor",
             "id": "/nacionales",
             "limit": "5",
             "offset": 15,
             "sort": "display_date:desc",
             "uri": "/nacionales/"}
    """

    def __init__(self, *args, **kwargs):
        self._data = None
        self._parameters = None
        self._query = None

    def set_parameters(self, parameters, query_args={}):
        self._parameters = parameters
        # This is just a basic query.
        self._query = {"arc-site": "abccolor",
             "id": "/nacionales",
             "limit": "5",
             "offset": 15,
             "sort": "display_date:desc",
             "uri": "/nacionales/"}
        self._query.update(query_args)

    def set_headers(self):
        pass

    def query(self, **query_args):
        query = self._query
        if query_args:
            query.update(**query_args)
        squery = "{"
        squery += ",".join(['"'+str(key)+'":"'+str(value)+'"' for key, value in query.items()])
        squery += "}"
        url = f'{self._parameters["base_url"]}{squery}'
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            raise requests.HTTPError((r.status_code, r.text))

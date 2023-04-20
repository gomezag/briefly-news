import requests
import json

DEFAULT_QUERY = {"arc-site": "abccolor",
                 "id": "/nacionales",
                 "limit": "5",
                 "offset": 15,
                 "sort": "display_date:desc",
                 "uri": "/nacionales/"}


class ABCScraper:

    def set_parameters(self, parameters, query_args={}):
        self._parameters.update(parameters)
        self._query.update(query_args)

    def set_headers(self):
        pass

    def query(self, endpoint, **query_args):
        query = self._query
        if query_args:
            query.update(**query_args)
        url = f'{self._parameters["base_url"]}{endpoint}?'
        params = []
        for key, value in query.items():
            params.append(f'{key}={json.dumps(value)}')
        url += ",".join(params)
        r = requests.get(url)
        print(url)
        if r.status_code == 200:
            return r.json()
        else:
            raise requests.HTTPError((r.status_code, r.text))

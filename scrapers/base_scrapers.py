import json
import requests
import urllib.parse as urlparse


class ArcPublishingScraper:
    """
    Base query for ArcPublishing endpoints.
    It takes an endpoint and query arguments, which are set in the url as `?key=json.dumps(values)`
    The query method returns the response as is when the status_code is 200.
    Otherwise, it raises an HTTPError.

    """
    def set_headers(self):
        pass

    def query(self, endpoint, **query_args):
        query = self._query
        if query_args:
            query.update(**query_args)
        url = f'{urlparse.urljoin(self._parameters["website"], endpoint)}?'
        params = []
        for key, value in query.items():
            params.append(f'{key}={json.dumps(value)}')
        url += "&".join(params)
        r = requests.get(url)
        if r.status_code == 200:
            return r
        else:
            raise requests.HTTPError((r.status_code, r.text))


class HTMLScraper:
    def query(self, endpoint):
        url = urlparse.urljoin(self._parameters['website'], endpoint)
        res = requests.get(url)

        return res

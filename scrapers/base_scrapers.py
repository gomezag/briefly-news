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
        try:
            self.lock.acquire()
            r = requests.get(url, timeout=30)
        finally:
            self.lock.release()
        if r.status_code == 200:
            return r
        else:
            raise requests.HTTPError((r.status_code, r.text))


class HTMLScraper:

    def query(self, endpoint):
        url = urlparse.urljoin(self._parameters['website'], endpoint)
        try:
            self.lock.acquire()
            res = requests.get(url, timeout=5)
        finally:
            self.lock.release()

        return res

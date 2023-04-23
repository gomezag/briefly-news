import json
import requests
import urllib.parse as urlparse


class ArcPublishingScraper:
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

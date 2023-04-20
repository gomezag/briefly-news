import requests
import json


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
        if r.status_code == 200:
            return r.json()
        else:
            raise requests.HTTPError((r.status_code, r.text))

    def get_headlines(self, category, *args, **kwargs):
        endpoint = self.endpoints.get('headlines', None)
        if not endpoint:
            raise ValueError(f'Headlines endpoint not defined for {self.__class__}')
        query = endpoint['data']
        query['query'].update(category)
        url = endpoint['path']
        r = self.query(url, **query)
        return r['content_elements']

    def get_categories(self, *args, **kwargs):
        endpoint = self.endpoints.get('categories', None)
        if not endpoint:
            raise ValueError(f'Category endpoint not defined for {self.__class__}')

        query_data = endpoint.get('data', {})
        data = self.query(endpoint['path'], **query_data)['children']
        r = []
        for el in data:
            try:
                url = el['site']['site_url']
                if not url.startswith('/'):
                    url = '/'+url
                if not url.endswith('/'):
                    url = url+'/'
                r.append({'id': el['_id'], 'uri': url})
            except (KeyError, AttributeError):
                pass
        return r

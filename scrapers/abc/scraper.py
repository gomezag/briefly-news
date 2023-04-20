import pandas as pd
import requests
import json


class ABCScraper:
    def __init__(self, *args, **kwargs):
        self.site = 'abc'
        self._categories = None
        self._data = pd.DataFrame()
        self._query = {}
        self._parameters = {}
        self.load_parameters()

    def set_headers(self):
        pass

    def load_categories(self, *args, **kwargs):
        try:
            categories = pd.read_csv(f'data/{self.site}/categories.csv')
            categories = [{'id': cat[1].values[1], 'uri': cat[1].values[2]} for cat in categories.iterrows()]
            return categories
        except FileNotFoundError:
            return None

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
        """
        Get the latest headlines
        :param category: a dictionary with an 'id' and 'uri' field
        :param kwargs: extra arguments will be updated in the query dictionary, such as limit
        :return: a list with the results.
        """
        endpoint = self.endpoints.get('headlines', None)
        if not endpoint:
            raise ValueError(f'Headlines endpoint not defined for {self.__class__}')
        query = endpoint['data']
        query['query'].update(category)
        query['query'].update(**kwargs)
        url = endpoint['path']
        r = self.query(url, **query)
        headlines = r['content_elements']
        return headlines, r

    def get_categories(self, *args, **kwargs):
        """
        Get the categories as a dataframe with the query parameters to get the headlines.
        :param args:
        :param kwargs:
        :return:
        """
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

    @property
    def categories(self):
        if not self._categories:
            self._categories = self.load_categories()
        return self._categories

    @property
    def parameters(self):
        return self._parameters
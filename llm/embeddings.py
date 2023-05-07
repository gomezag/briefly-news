import pandas as pd
import openai
import time
import logging
import os

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from database.xata_api import XataAPI

load_dotenv()

logger = logging.getLogger(__name__)
openai.organization = os.getenv('OPENAI_ORG')
openai.api_key = os.getenv('OPENAI_KEY')


def get_embedding(text, model="text-embedding-ada-002", embed=True):
    """
    Util function to generate an embedding using OpenAI api.
    the text is a list of elements. Each row will be stringified using BeautifulSoup, and concatenated
    together. The resulting text will be used to generate the embedding.

    Inputs:

        :param text: text to embed
        :param model: model to use. default: ada-002
        :param embed: flag to actually embed the text. The embedding is set to None otherwise.

    Output:

        :return: a truplet with the embedding, process time, token number.

    """
    st_time = time.time()

    out = ''
    for t in text:
        out += str(BeautifulSoup(t, 'html.parser').text)
        out += " "
    out = out.replace("\n", " ")
    if embed:
        embedding = openai.Embedding.create(input=[out], model=model)
        tokens = embedding['usage']['total_tokens']
        return embedding['data'][0]['embedding'], time.time() - st_time, tokens
    else:
        return None, time.time() - st_time, None


class Embedder(object):
    """
    Embedder object.
    """
    def __init__(self, **kwargs):
        branch = kwargs.pop('branch', 'main')
        self._db = XataAPI(branch=kwargs.pop('branch', branch))

    def embed_nonembedded_articles(self, limit=1, update=True, embed=True):
        """
        Query the database for articles without embeddings, generate an embedding for them,
        and update the database entry.

        Inputs:

            :param limit: article limit to update. default: 1
            :param update: flag to update entries in the databaes. default: True
            :param embed: flag to generate the embeddings. default: True

        Output:

            :return: a pandas DataFrame with the embedded articles.

        """
        logging.info(f"Embedding unembedded articles")
        table = 'news_article'
        articles = self._db.query(table,
                                  filter={'$notExists': 'embedding',
                                          '$exists': 'article_body'},
                                  sort={'date': 'desc'},
                                  page={'size': limit})['records']
        logging.info(f"Found {len(articles)} total.")
        print([a['id'] for a in articles])
        if limit < len(articles):
            logging.info(f"Limiting to {limit} results.")
        else:
            limit = len(articles)
        articles = articles[:limit]
        return self.embed_articles(articles, update=update, embed=embed, keys=['date', 'title', 'subtitle', 'article_body'])

    def embed_articles(self, articles, update=True, embed=True, keys=None):
        """
        Embed a list of articles.

        Inputs:

            :param articles: A list of articles. Each article is a dictionary with valid values.
            :param update: flag to update elements in database after embedding
            :param embed: flag to perform embedding (incur in OpenAI costs).
            :param keys: keys to include in the embedding.

        Output:

            :return: A pandas dataframe with the embedded articles.

        """
        limit = len(articles)
        table = 'news_article'

        df = pd.DataFrame(articles)
        if keys:
            qdf = df[keys]
        else:
            qdf = df
        qdf = qdf.astype(str)
        results = qdf.apply(lambda x: pd.Series(get_embedding(x, model='text-embedding-ada-002', embed=embed)), axis=1)
        results.columns = ['embedding', 'process_time', 'tokens']
        rdf = pd.concat([df[['id']], results[['embedding', 'process_time', 'tokens']]], axis=1)
        embedded_articles = rdf.to_dict('records')
        for i, record in enumerate(embedded_articles):
            record_id = record.pop('id')
            if i % 5 == 0:
                logger.info(f'Embedding {i}/{limit}')
            if update:
                self._db.update(table, record_id, record)
        return df

    @property
    def vectors(self):
        return self._data['embedding']

    @property
    def cost(self):
        return self._data['process_time']


import pandas as pd
import openai
import time
import logging
import os

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from database.xata_api import XataAPI
from llm.utils import get_related_people

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
        return embedding['data'][0]['embedding'], tokens
    else:
        return None, None


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
            :param update: flag to update entries in the database. default: True
            :param embed: flag to generate the embeddings. default: True

        Output:

            :return: a pandas DataFrame with the embedded articles.

        """
        logging.info(f"Embedding unembedded articles")
        table = 'news_article'
        if limit > 200:
            done = 0
            articles = []
            page = 1
            while done < limit:
                articles.extend(
                    self._db.query(table,
                                   filter={'$notExists': 'embedding',
                                           '$exists': 'article_body'},
                                   sort={'date': 'desc'},
                                   columns=('date',
                                            'title',
                                            'subtitle',
                                            'article_body',
                                            'authors',
                                            'source',
                                            'publisher.publisher_name'),
                                   page={'size': 200, 'offset': done})['records']
                )
                page += 1
                done += 200
            articles = articles[:limit]
        else:
            articles = self._db.query(table,
                                      filter={'$notExists': 'embedding',
                                              '$exists': 'article_body'},
                                      sort={'date': 'desc'},
                                      columns=('date',
                                               'title',
                                               'subtitle',
                                               'article_body',
                                               'authors',
                                               'source',
                                               'publisher.publisher_name'),
                                      page={'size': limit})['records']
        logging.info(f"Found {len(articles)} total.")
        if limit < len(articles):
            logging.info(f"Limiting to {limit} results.")
        else:
            limit = len(articles)
        articles = articles[:limit]
        for article in articles:
            article.update({
                'article_body': BeautifulSoup(article['article_body'], 'html.parser').text,
                'publisher': article['publisher']['publisher_name'],
                'source': article.get('source', article['publisher']['publisher_name']),
            })
        i = 0
        while articles:
            if i % 5 == 0:
                logger.info(f'Embedding {i}/{limit}')
            article = articles.pop(0)
            try:
                self.embed_articles([article], update=update, embed=embed, keys=['date',
                                                                                   'title',
                                                                                   'subtitle',
                                                                                   'article_body',
                                                                                   'authors',
                                                                                   'source',
                                                                                   'publisher'])
            except Exception as e:
                print(repr(e))
                pass
            i += 1

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
        results.columns = ['embedding', 'tokens']
        rdf = pd.concat([df[['id']], results[['embedding', 'tokens']]], axis=1)
        embedded_articles = rdf.to_dict('records')
        for i, record in enumerate(embedded_articles):
            record_id = record.pop('id')
            if update:
                self._db.update(table, record_id, record)
        return df

    @property
    def vectors(self):
        return self._data['embedding']

    @property
    def cost(self):
        return self._data['process_time']


class Tagger(object):
    """
    Tagger object.
    """
    def __init__(self, **kwargs):
        branch = kwargs.pop('branch', 'main')
        self._db = XataAPI(branch=kwargs.pop('branch', branch))

    def tag_untagged_articles(self, limit=1, update=True):
        """
        Query the database for articles without tags, generate the tags for them,
        and update the database entry.

        Inputs:

            :param limit: article limit to update. default: 1
            :param update: flag to update entries in the database. default: True
            :param embed: flag to generate the tags. default: True

        Output:

            :return: a pandas DataFrame with the tagged articles.

        """
        logging.info(f"Tagging untagged articles")
        table = 'news_article'
        articles = self._db.query(table,
                                  filter={'$notExists': 'POIs',
                                          '$exists': 'article_body'},
                                  sort={'date': 'desc'},
                                  page={'size': limit})['records']
        for article in articles:
            article['publisher'] = article['publisher']['id']
        logging.info(f"Found {len(articles)} total.")
        if limit < len(articles):
            logging.info(f"Limiting to {limit} results.")
        else:
            limit = len(articles)
        articles = articles[:limit]
        counts, articles = get_related_people(articles, 'PER')
        for i, record in enumerate(articles):
            record_id = record.pop('id')
            record.pop('xata', None)
            pois_ids = []
            for poi in record['POIs']:
                poi, c = self._db.get_or_create('POI', {'label': poi})
                pois_ids.append(poi['id'])
                articles = poi.get('articles', [])
                articles.append(record_id)
                articles = list(set(articles))
                poi.update({'articles': articles})
                pid = poi.pop('id')
                poi.pop('xata', None)
                self._db.update('POI', pid, poi)
            record['POIs'] = list(set(record['POIs']))

            if i % 5 == 0:
                logger.info(f'Tagged {i}/{limit}')
            if update:
                self._db.update(table, record_id, record)
            else:
                logger.info(f"Skipping {record_id}, with info {record}.")
        return articles

import pandas as pd
import openai
import time
import logging
import os

from dotenv import load_dotenv

from database.xata_api import XataAPI

load_dotenv()

logger = logging.getLogger('__name__')
openai.organization = os.getenv('OPENAI_ORG')
openai.api_key = os.getenv('OPENAI_KEY')


def get_embedding(text, model="text-embedding-ada-002"):
   st_time = time.time()

   out = ''
   for t in text:
      out += str(t)
   out = out.replace("\n", " ")

   embedding = openai.Embedding.create(input=[out], model=model)

   return embedding['data'][0]['embedding'], time.time() - st_time


class Embedder(object):
   def __init__(self, **kwargs):
      self._db = XataAPI(branch=kwargs.pop('branch', 'main'))

   def embed_nonembedded_articles(self, limit=1):
      articles = self._db.query('news_article', filter={'$notExists': 'embedding'}, sort={'date':'desc'})
      df = pd.DataFrame(articles)
      df = df[['date', 'title', 'subtitle']]
      df = df.astype(str)
      results = df.apply(lambda x: pd.Series(get_embedding(x, model='text-embedding-ada-002')), axis=1)
      results.columns = ['embedding', 'process_time']
      df = pd.concat([df, results], axis=1)

      return df

   @property
   def vectors(self):
      return self._data['embedding']

   @property
   def cost(self):
      return self._data['process_time']

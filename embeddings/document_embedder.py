import pandas as pd
import openai
import time
import logging
import os

from dotenv import load_dotenv

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


class EmbeddingGroup(object):

   def __init__(self):
      self._data = None

   def read_file(self, file):
      """
      Read a file
      :param file:
      :return:
      """
      df = pd.read_csv(file)
      df.columns=['date', 'title', 'article_body', '...']  # What else?

      return df

   def create_embedding(self, chunk):
      """

      :param chunk: A pandas dataframe with only text in the columns
      :return:
      """
      results = chunk.apply(lambda x: pd.Series(get_embedding(x, model='text-embedding-ada-002')), axis=1)
      results.columns = ['embedding', 'process_time']  # No of tokens, etc..
      results.to_csv('output/embedded_data.csv', index=False)

      self._data = results

   @property
   def vectors(self):
      return self._data['embedding']

   @property
   def cost(self):
      # Here we can get fancy with price  calculation
      return self._data['process_time']


class Chat:
   def __init__(self, n):
      self.n = n
      self.messages = []

   def chat(self, message):
      self._add_msg({'role': 'user', 'content': message})
      response = self._generate_chat()
      self._add_msg({'role': 'assistant', 'content': response})

      return response

   def _add_msg(self, message_data):
      self.messages.append(message_data)
      while len(self.messages) > self.n:
         self.messages.pop(0)

   def _generate_chat(self):

      return openai.ChatCompletion.create(
         model='gpt-3.5-turbo',
         messages=self.messages
      )


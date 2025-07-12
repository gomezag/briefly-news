import logging
import time

import es_core_news_md
import pandas as pd
from bs4 import BeautifulSoup

nlp = es_core_news_md.load()
categories = ['política', 'economía', 'sociedad', 'cultura', 'deportes', 'tecnología', 'medio ambiente']

def get_related_people(articles, type):
    """
    Tags articles by joining their title, subtitle and body and removing HTML tags with BeautifulSoup.

    Then uses spacy lib to tag words and returns a list of words with tag matching `type`.

    Inputs:

        :param articles:
        :param type:

    Output:

        :return: related, articles
            - :related: A list of words with matching tags with the # of times they appear in the articles.
            - :articles: The article list with an extra column including the list of words with matching tags that
            appear in the article.
    """
    data = []
    st_time = time.time()

    for i, article in enumerate(articles):
        related_persons = []
        title = article.get('title', '')
        subtitle = article.get('subtitle', '')
        body = article.get('article_body', '')
        text = BeautifulSoup(' '.join([title, subtitle, body]), 'html.parser').text
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == type and str(ent) != 'Lea':
                related_persons.append(str(ent).upper().title())
        category_similarities = []
        for cat in categories:
            category_similarities.append(nlp(cat).similarity(doc))
        category = categories[category_similarities.index(max(category_similarities))]
        related_persons = list(set(related_persons))
        data.append([article.get('id', None), article['url'], related_persons])
        article.update({'POIs': related_persons, 'category': category, 'body_vector': doc.vector.tolist()})
    related_table = pd.DataFrame(columns=['id', 'url', 'names'], data=data)
    related = related_table[['names']].explode('names').groupby('names').value_counts().reset_index().sort_values('count',ascending=False)
    seconds = time.time() - st_time
    logging.debug(f'Tagged articles in {seconds} seconds.')
    return related, articles

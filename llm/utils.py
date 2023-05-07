import pandas as pd
import es_core_news_md
from bs4 import BeautifulSoup

nlp = es_core_news_md.load()


def get_related_people(articles, type):
    data = []
    for i, article in enumerate(articles):
        related_persons = []
        title = article.get('title', '')
        subtitle = article.get('subtitle', '')
        body = article.get('article_body', '')
        text = BeautifulSoup(' '.join([title, subtitle, body]), 'html.parser').text
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == type and str(ent)!='Lea':
                related_persons.append(str(ent))

        data.append([article['id'], article['url'], related_persons])
        article.update({'names': related_persons})
    related_table = pd.DataFrame(columns=['id', 'url', 'names'], data=data)
    related = related_table[['names']].explode('names').groupby('names').value_counts().reset_index().sort_values('count',ascending=False)
    return related, articles


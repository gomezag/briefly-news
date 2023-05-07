# LLM

## Embedder class

    from database.xata_api import XataAPI
    from llm.embeddings import Embedder

    embedder = Embedder(branch='dev')
    xata = XataAPI(branch='dev')
    res = xata.query('news_article',   filter={'$exists':'article_body'})
    articles = res['records']
    embedder.embed_articles(articles)
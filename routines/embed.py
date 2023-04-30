import sys
import logging

from embeddings import Embedder


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    branch = sys.argv[1]
except IndexError:
    branch = 'main'

try:
    limit = int(sys.argv[2])
except IndexError:
    limit = 15


for site in ['abc', ]:
    try:
        logger.info(f'Starting embedding for site {site} on branch {branch}.')
        logger.info(f'Limiting to {limit} results.')
        embedder = Embedder(branch=branch)
        embedder.embed_nonembedded_articles(limit=limit)
    except Exception as e:
        print(repr(e))

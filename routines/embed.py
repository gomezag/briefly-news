import sys
import logging

from llm import Embedder


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    logging.root.setLevel(logging.INFO)

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
            logging.info(f'Starting embedding for site {site} on branch {branch}.')
            logging.info(f'Limiting to {limit} results.')
            embedder = Embedder(branch=branch)
            while limit > 1000:
                embedder.embed_nonembedded_articles(limit=1000)
                limit -= 1000
            embedder.embed_nonembedded_articles(limit=limit)
        except Exception as e:
            print(repr(e))

import sys
import logging

from llm import Tagger


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

    try:
        logging.info(f'Tagging started on branch {branch}.')
        logging.info(f'Limiting to {limit} results.')
        tagger = Tagger(branch=branch)
        chunks = limit//200
        while limit > 200:
            logging.info(f'')
            tagger.tag_untagged_articles(limit=200, update=True)
            limit = limit - 200
    except Exception as e:
        print(repr(e))

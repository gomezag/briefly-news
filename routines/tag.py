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

    for site in ['abc',]:
        try:
            logging.info(f'Tagging started for site {site} on branch {branch}.')
            logging.info(f'Limiting to {limit} results.')
            tagger = Tagger(branch=branch)
            tagger.tag_untagged_articles(limit=limit, update=True)
        except Exception as e:
            print(repr(e))

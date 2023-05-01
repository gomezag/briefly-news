import pytest
from llm.embeddings import Embedder


@pytest.fixture
def embedder():
    yield Embedder(branch='dev')

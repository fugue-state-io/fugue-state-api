import pytest
from .. import src
@pytest.fixture
def app():
    app = src.app

    yield app

@pytest.fixture
def client(app):
    return app.test_client()
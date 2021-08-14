import pytest
from ktc import app
import json


@pytest.fixture
def client():
    return app.app.test_client()


def test_environments_gives_json_with_proper_mimetype(client):
    response = client.get("/api/environments")
    assert response.status_code == 200
    assert response.content_type == 'application/json'


def test_environments_gives_correct_list(client):
    environments_expected = ['aquatic', 'arctic', 'cave', 'coast', 'desert', 'dungeon', 'forest',
                                        'grassland', 'mountain', 'planar', 'ruins', 'swamp', 'underground', 'urban']
    response = client.get("/api/environments")
    environments_received = response.get_json()

    assert environments_received == environments_expected

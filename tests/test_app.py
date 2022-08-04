import flask
import json
import os
import pytest

from app import configure_routes

@pytest.fixture
def client():
    app = flask.Flask(__name__)
    configure_routes(app)
    client = app.test_client()

    return client


def test_base_route(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.get_data() == b'Flask picoscope server running'


def test_random_route_failure(client):
    response = client.get('/some_nonexistent_url')
    assert response.status_code == 404


def test_logs():
    assert os.path.isfile('logs/logs.log')


def test_connection(client):
    response = client.get('/connect')

    assert response.status_code == 200
    assert response.get_data() == b'Picoscope connected'


def test_sweep(client, params):
    response = client.post('/get_resonance', data=params)

    data = json.loads(response.get_data())

    assert response.status_code == 200
    assert isinstance(data, list)


def test_disconnect(client):
    response = client.get('/disconnect')

    assert response.status_code == 200
    assert response.get_data() == b'Picoscope disconnected'

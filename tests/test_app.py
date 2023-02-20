from dataclasses import asdict
import flask
from flask.testing import FlaskClient
import json
import os
import pytest

from picoscope.constants import PulsingParams
from app import configure_routes

pulsing_params: PulsingParams = PulsingParams(
    delay = 26,
    voltage = 1,
    duration = 8,
    avg_num = 32
)

@pytest.fixture
def base_client():
    app = flask.Flask(__name__)
    configure_routes(app)
    client = app.test_client()

    return client


def test_base_route(base_client: FlaskClient):
    response = base_client.get('/')

    assert response.status_code == 200
    assert response.get_data() == b"Flask picoscope server running."


def test_random_route_failure(base_client: FlaskClient):
    response = base_client.get('/some_nonexistent_url')
    assert response.status_code == 404


def test_logs():
    assert os.path.isfile('logs/logs.log')

@pytest.fixture
def client_with_yield():
    app = flask.Flask(__name__)
    configure_routes(app)
    client = app.test_client()

    yield client   

    client.get('/disconnect')

def test_connect(client_with_yield: FlaskClient):
    response = client_with_yield.get('/connect')

    assert response.status_code == 200
    assert response.get_data() == b"Picoscope status: connected."


@pytest.fixture
def client_with_pico_connected_yield(base_client: FlaskClient):
    base_client.get('/connect')

    yield base_client

    base_client.get('/disconnect')


def test_pulse(client_with_pico_connected_yield: FlaskClient):
    response = client_with_pico_connected_yield.post('/get_wave', data=asdict(pulsing_params))

    assert response.status_code == 200
    assert isinstance(json.loads(response.get_data()), dict)



@pytest.fixture
def client_with_pico_connected_no_yield(base_client: FlaskClient):
    base_client.get('/connect')

    return base_client


def test_disconnect(client_with_pico_connected_no_yield: FlaskClient):
    response = client_with_pico_connected_no_yield.get('/disconnect')

    assert response.status_code == 200
    assert response.get_data() == b'Picoscope disconnected.'

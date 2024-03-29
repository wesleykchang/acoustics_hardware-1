from dataclasses import asdict
import flask
from flask.testing import FlaskClient
import json
import os
import pytest
from time import time

from picoscope.parameters import PulsingParams
from app import configure_routes

pulsing_params: PulsingParams = PulsingParams(
    delay = 26,
    voltage_range = 1,
    duration = 8
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
    assert response.get_data() == b"Flask picoscope server running. Picoscope connection status: 0"


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
    assert response.get_data() == b"Picoscope connection status: 1"


def test_is_not_connected(base_client: FlaskClient):
    response = base_client.get('/is_connected')

    assert response.status_code == 200
    assert response.get_data() == b"Picoscope connection status: 0"


@pytest.fixture
def client_with_pico_connected_yield(base_client: FlaskClient):
    base_client.get('/connect')
    start_time = time()

    yield base_client

    end_time = time()
    time_elapsed = end_time - start_time
    print(f'The pulse took {round(time_elapsed, 2)*1000} ms.')

    base_client.get('/disconnect')


def test_is_connected(client_with_pico_connected_yield: FlaskClient):
    response = client_with_pico_connected_yield.get('/is_connected')

    assert response.status_code == 200
    assert response.get_data() == b"Picoscope connection status: 1"


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

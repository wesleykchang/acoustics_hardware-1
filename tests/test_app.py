import flask
import json
import os
import pytest

from app import configure_routes

params = {
    'start_freq': 1000.0,
    'end_freq': 19000.0,
    'increment': 100.0,
    'dwell': .001,
    'voltage': 0.2,
    'sweep_interval': 150,
    'c_rate': 1 / 2.,
    'no_cycles': 1,
    'warm_up': 60,
    'rest': 60,
    'channel': 0,
    'voltage_range': 1.0
}

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


def test_logs():
    assert os.path.isfile('logs/logs.log')

def test_connection(client):
    response = client.get('/connect')

    assert response.status_code == 200
    assert response.get_data() == b'Picoscope connected'

def test_sweep(client):
    response = client.post('/get_resonance', data=params)

    data = json.loads(response.get_data())

    assert response.status_code == 200
    assert isinstance(data, list)

def test_close(client):
    response = client.get('/disconnect')

    assert response.status_code == 200
    assert response.get_data() == b'Picoscope disconnected'

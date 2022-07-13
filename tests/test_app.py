import flask
import json
import pytest

from app import configure_routes

params = {
    'exp_name': 'Kokam-000-2022-04-06',
    'start_freq': 1000,
    'end_freq': 21000,
    'increment': 100,
    'dwell': .001,
    'voltage': 0.2,
    'sweep_interval': 150,
    'c_rate': 1 / 2.,
    'no_cycles': 1,
    'warm_up': 60,
    'rest': 60
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

def test_connection(client):
    response = client.get('/connect')

    assert response.status_code == 200
    assert response.get_data() == b'Picoscope connected'

def test_sweep(client):
    _ = client.get('/connect')
    response = client.post('/get_resonance', data=params)
    
    assert response.status_code == 200
    assert isinstance(response.get_data(), list)

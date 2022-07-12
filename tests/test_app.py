import pytest

from picoscope import app

def test_app():
    with app() as app_:
        response = app_.get('/')
        assert response.status_code == 200
        assert b"Flask picoscope server running" in response.data

@pytest.mark.integtest
def test_picoscope_connection():
    with app() as app_:
        response = app_.get('/connect')
        assert response.status_code == 200
        assert b"Picoscope connected" in response.data

@pytest.mark.integtest
def test_sweep():
    with app() as app_:
        response = app_.get('get_resonance')
        assert response.status_code == 200
        assert isinstance(response.data, list)
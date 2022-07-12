import pytest

import app.app as app

@pytest.fixture
def test_app():
    return app.test_client()

# @pytest.mark.integtest
# def test_picoscope_connection():
#     with app() as app_:
#         response = app_.get('/connect')
#         assert response.status_code == 200
#         assert b"Picoscope connected" in response.data

# @pytest.mark.integtest
# def test_sweep():
#     with app() as app_:
#         response = app_.get('get_resonance')
#         assert response.status_code == 200
#         assert isinstance(response.data, list)
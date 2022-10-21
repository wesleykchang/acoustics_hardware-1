"""Setting up testing suite. Autoruns before every test session."""

import json
import pickle
import pytest

@pytest.fixture(scope='session')
def params():
    with open("tests/params.json") as f:
        params = json.load(f)

    return params

@pytest.fixture(scope='session')
def picodata():
    with open('tests/data/waveform.pkl', 'rb') as f:
        picodata = pickle.load(f)

    return picodata
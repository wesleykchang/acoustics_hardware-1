import pickle

from picoscope import picoplot

with open('tests/data/waveform', 'wb') as f:
    picodata = pickle.load(f)


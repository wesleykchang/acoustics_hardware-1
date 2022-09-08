# Acoustics Hardware

This package contains functionality for remotely and programmatically controlling oscilloscopes from Picotech. It is written and maintained by the acoustics team at [Club Steingart](https://lab.dansteingart.com/).

Module `picoscope/picoscope.py` can be run as a standalone program. However, it is optimized for being run containerized as a webserver where it is controlled via http requests. In lab we run it through proftron Dan's [pithy](https://github.com/steingart/pithy). YMMV.

Branch `dev` is actively maintained. At the time of writing it only has an implementation for resonance with 4000-level picoscopes. Branch `legacy` is kept for backwards compatibility with the old docker build. It contains a working implementation for 2000-level picoscopes which we use for pulsing. 

```
./
├── app.py
├── picoscope
│   ├── dft.py
│   ├── picoplot.py
│   ├── picoscope.py
│   ├── settings.json
│   ├── sweep.py
│   └── utils.py
├── README.md
├── requirements.txt
├── tests
    ├── conftest.py
    ├── __init__.py
    ├── params.json
    ├── test_dft.py
    ├── test_picoplot.py
    ├── test_picoscope.py
    ├── test_sweep.py
    └── test_utils.py

```

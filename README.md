# Acoustics Hardware

### Overview

This package contains functionality for remotely and programmatically interfacing with oscilloscopes from Picotech, so-called Picoscopes. It is written and maintained by the acoustics team at [Club Steingart](https://lab.dansteingart.com/).

Module `picoscope/pulse.py` can be run as a standalone program. However, it is optimized for being run [containerized](https://www.docker.com/) as a webserver where it is controlled via the `http` protocol. In lab we do it through proftron Dan's [pithy](https://github.com/steingart/pithy). YMMV.

There are three branches, two of which are actively maintained:

1. Branch `pulsing` is written and maintained for pulsing with 2000a-level Picoscopes.

2. Branch `resonance` is written and maintained for performing resonance with 4000-level Picoscopes.

3. Branch `legacy` is kept for posterity with the old docker build. It contains working implementations for a variety of oscilloscopes, including Epoch, SIUI etc.

### Structure

```
./
├── app.py
├── picoscope
│   ├── constants.py
│   ├── parameters.py
│   ├── picoscope.py
│   ├── pulse.py
│   └── utils.py
├── README.md
├── requirements.txt
├── tests
    ├── __init__.py
    ├── test_app.py
    ├── test_parameters.py
    ├── test_picoscope.py
    ├── test_pulse.py
    └── test_utils.py

```

### Setup

Setting up the picoscope drivers is a pain, which is why one should utilize the `Dockerfile`,

```
$ docker build . -t pico
```

After building the image, the container should be launched in privileged mode, with `picoscope.constants.port` exposed. This can be done manually from the command line, but preferably with a nice `docker-compose.yaml`. Ours is roughly like this:

```
"version": "3"
services:
  pico:
    container_name: pico
    image: pico
    ports:
      - 5001:5001
    volumes:
      - /dev/:/dev/
      - acoustics_hardware:/acoustics_hardware/
    restart: on-failure:10
    privileged: true
    tty: true
    networks:
      acoustics-network:
        ipv4_address: 192.168.0.10

  pulser:
    container_name: pulser
    image: nodeforwarder
    ports:
      - 9002:9002
    environment:
      - serial_port=/dev/ttyUSB0
      - internet_port=9002
      - baud_rate=9600
    volumes:
      - /dev/:/dev/
    privileged: true
    tty: true
    # stdin_open: true
    networks:
      acoustics-network:
        ipv4_address: 192.168.0.20

volumes:
  acoustics_hardware:
networks:
  acoustics-network:
    ipam:
      config:
        - subnet: 192.168.0.0/24

```

We want the oscilloscope and pulser to be hosted separately because the resultant modularity is more robust, hence the `pulser` container. We use pulsers from Ultratek. Refer to [nodeforwarder](https://github.com/steingartlab/nodeforwarder) for details on how to control it (and the Picoscope+Pulser Notion Lab Manual).

Beware that this allows anyone with knowledge of the computer's IP and the port exposed on the container to control it. As such, you should ensure both your computer and the one hosting the Picoscope server are on a secured network. We use Zerotier. 

# Usage

Okay, so now you have two containers running on a network, one controlling the oscilloscope and another the pulser. Do note that one of the picoscope channels must be connected to the pulser's _trigger_. If you're a Steingartian refer again to the Notion Lab Manual for the hardware connection.

A minimum reproducible code sample (we prefer python) is as follows (pulser code omitted)

```
from dataclasses import dataclass, asdict
import requests
from typing import Dict, List

import database
import pithy3 as pithy

IP = '192.168.0.1'
PORT = '9001'


@dataclass
class PulsingParams:
    """All the params that should should be passed
    to a pulsing picoscope, no more, no less.

    Change at your leisure.
    """

    delay: int = 10
    voltage_range: int = 5
    duration: int = 5


def get_data_from_oscilloscope(PulsingParams_: PulsingParams, ip_: str, port: str) -> Dict[str, List[float]]:
    """Queries data from oscilloscope.
    
    Args:
        PulsingParams (dataclass): See definition at top of module. 
        ip_ (str, optional): IP address of oscilloscope container.
            Defaults to '192.168.0.1'.
        port (str, optional): Exposed port of oscilloscope container.
            Defaults to '5001'.
    
    Returns:
        dict[str: list[float]]: Single key-value pair with key='data' and value
            acoustics pulse data.
    """

    url = f'http://{ip_}:{port}/get_wave'
    pulsing_params: dict = asdict(PulsingParams_)
    response = requests.post(url, data=pulsing_params).text
    
    data = json.loads(response)
    
    return data
            
    
def pulse(PulsingParams_: PulsingParams = None) -> Dict[str, List[float]]:
    """Wrapper for acoustic pulsing.

    Only module function that should be called externally.
    
    Args:
        PulsingParams (dataclass, optional): Pulsing parameters. 
    """
    
    if PulsingParams_ is None:
        PulsingParams_ = PulsingParams()
    
    pulser = Pulser()  # paying the initialization tax bc it's more reliable
    pulser.turn_on()
    waveform = get_data_from_oscilloscope(PulsingParams_=PulsingParams_)
    pulser.turn_off()
    
    return data
        
    
def main():
    data = pulse()
    
if __name__ == "__main__":
    main()

```

And there you go, Bob's your uncle.
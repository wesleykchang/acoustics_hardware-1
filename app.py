"""Flask app connecting pithy container to picoscope container"""

import flask
import json
import logging
import os
from typing import Dict, List
from werkzeug.exceptions import BadRequest

from picoscope.parameters import PulsingParams
from picoscope.picoscope import Picoscope2000
from picoscope import pulse
from picoscope.utils import bool_to_requests, dataclass_from_dict, parse_dict_vals


log_filename = "logs/logs.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s: %(message)s'
)

PORT: int = 5001  # TODO: Move to an env variable

app: flask.Flask = flask.Flask(__name__)
picoscope_: Picoscope2000 = Picoscope2000()


def picoscope_status() -> str:
    return f"Picoscope connection status: {bool_to_requests(picoscope_.is_connected)}"


def configure_routes(app):

    @app.route('/')
    def hello_world():
        """
        Returns:
            Str: Status message
        """
        return f"Flask picoscope server running. {picoscope_status()}"

    @app.route('/connect')
    def connect():
        """Separated from startup to be able to restart if connection is lost
        w/o having to restart container.
        """

        picoscope_.connect()  # Calls self.is_connected() implicitly

        return picoscope_status()

    @app.route('/is_connected')
    def is_connected():
        """Checking whether picoscope is connected."""

        picoscope_.is_connected

        return picoscope_status()

    @app.route('/get_wave', methods=['POST'])
    def pulsing():
        """Pulsing. Performs a pulse and returns the resulting data.
        
        Returns:
            dict: Pulsing data.
        """

        raw_pulsing_params: Dict[str, str] = flask.request.values.to_dict()
        pulsing_params_parsed: Dict[str, float] = parse_dict_vals(dict_=raw_pulsing_params)
        pulsing_params_: PulsingParams = dataclass_from_dict(
            dict_=pulsing_params_parsed,
            dataclass_=PulsingParams
        )
        payload: Dict[str, List[float]] = pulse.pulse(
            picoscope_=picoscope_,
            pulsing_params=pulsing_params_
        )

        return json.dumps(payload)

    @app.route('/disconnect')
    def disconnect():
        """Disconnects the oscilloscope. Mainly for testing purposes."""
        picoscope_.disconnect()

        return 'Picoscope disconnected.'

    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return '', 404


configure_routes(app)

if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0", debug=False)


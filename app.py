"""Flask app connecting pithy container to picoscope container"""

import flask
import json
import logging
import os
from typing import Dict
from werkzeug.exceptions import BadRequest

from picoscope.constants import PulsingParams
from picoscope.picoscope import Picoscope2000
from picoscope import techniques
from picoscope.utils import parse_incoming_params


log_filename = "logs/logs.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s: %(message)s'
)

PORT: int = 5001

app = flask.Flask(__name__)


def configure_routes(app):

    @app.route('/')
    def hello_world():
        """
        Returns:
            Str: Status message
        """
        return "Flask picoscope server running."

    @app.route('/connect')
    def connect():
        """Am separating from startup to be able to restart if connection is lost
        w/o having to restarting container
        """
        global picoscope_

        picoscope_ = Picoscope2000()
        picoscope_.connect()
        is_connected_ = picoscope_.is_connected()

        status = '' if is_connected_ else 'not '

        return f'Picoscope status: {status}connected.'

        
    @app.route('/get_wave', methods=['POST'])
    def pulse():
        """Pulsing. Performs a pulse and returns the resulting data.
        
        Returns:
            dict: Pulsing data.
        """

        raw_incoming_params: Dict[str, str] = flask.request.values.to_dict()
        pulsing_params: PulsingParams = parse_incoming_params(raw_params=raw_incoming_params)

        waveform = techniques.pulse(picoscope_=picoscope_, pulsing_params=pulsing_params)

        return json.dumps(waveform)

    @app.route('/disconnect')
    def disconnect():
        """Mainly for testing purposes. Disconnects the oscilloscope."""

        picoscope_.disconnect()

        return 'Picoscope disconnected.'

    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return '', 404


configure_routes(app)

if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0", debug=False)

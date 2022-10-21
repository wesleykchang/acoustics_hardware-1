"""Flask app connecting pithy container to picoscope container"""

import flask
import json
import logging
import os
import werkzeug

from picoscope.utils import parse_incoming_params

log_filename = "logs/logs.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(filename=log_filename,
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')

PORT = '5001'

app = flask.Flask(__name__)


def configure_routes(app):
    from picoscope.techniques import pulse, sweep
    from picoscope.picoscope import Picoscope2000, Picoscope4000

    @app.route('/')
    def hello_world():
        """
        Returns:
            Str: Status message
        """
        return "Flask picoscope server running"

    @app.route('/connect', methods=['POST'])
    def connect():
        """Connect to picoscope
    
        This is basically an initializer.
        Note that it oftentimes has to be rerun a couple of times before
        a connection is established.

        Returns:
            str: Status message
        """

        global picoscope_

        raw_params = flask.request.values.to_dict()

        picoscope_ = Picoscope2000() if raw_params['type_']=='2000' else Picoscope4000()

        picoscope_.connect()

        return "Picoscope connected"

    @app.route('/get_wave', methods=['POST'])
    def pulse():
        """Pulsing. Performs a pulse and returns the resulting data.
        
        Returns:
            dict: Pulsing data.
        """

        raw_params = flask.request.values.to_dict()
        params = parse_incoming_params(raw_params=raw_params)

        data = pulse(picoscope_=picoscope_, params=params)

        return json.dumps(data)

    # Runs resonance
    @app.route('/get_resonance', methods=['POST'])
    def get_resonance():
        """Resonance. Performs a frequency sweep and returns the resulting data.

        Returns:
            dict: Resonance data.
        """

        raw_params = flask.request.values.to_dict()
        params = parse_incoming_params(raw_params=raw_params)

        data = sweep(picoscope_=picoscope_, params=params)

        return json.dumps(data)

    @app.route('/disconnect')
    def disconnect():
        """Mainly for testing purposes. Disconnects the oscilloscope."""

        picoscope_.disconnect()

        return 'Picoscope disconnected'

    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(e):
        return '', 404


configure_routes(app)

if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0", debug=True)

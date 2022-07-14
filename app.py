"""Flask app connecting pithy container to picoscope container"""

import flask
import json
import logging
import os


log_filename = "logs/logs.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(filename=log_filename,
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')

PORT = '5001'

app = flask.Flask(__name__)


def configure_routes(app):
    from picoscope import picoscope

    #test to see that server is alive
    @app.route('/')
    def hello_world():
        """

        Returns:
            Str: Status message
        """
        return "Flask picoscope server running"

    @app.route('/connect')
    def connect():
        """Connect to picoscope
    
        This is basically an initializer.
        Note that it oftentimes has to be rerun a couple of times before
        a connection is established.

        Returns:
            str: Status message
        """
        picoscope.connect()

        return "Picoscope connected"

    @app.route('/pulse')
    def pulse():

        return "Pulsing hasn't been implemented"

    # Runs resonance
    @app.route('/get_resonance', methods=['POST'])
    def get_resonance():
        """This is where the magic happens.

        Receives params from pithy, passes them onto the oscilloscope,
        sweeps, and finally returns the data

        Returns:
            _type_: _description_
        """

        params_dict_w_strs = flask.request.values.to_dict()
        # Raw dict has this form {'value should be a float': '5.0'}
        params = dict([key, float(val)]
                      for key, val in params_dict_w_strs.items())

        data = picoscope.sweep(params=params)

        return json.dumps(data)

    @app.route('/disconnect')
    def disconnect():
        """Mainly for testing purposes. Disconnects the oscilloscope."""

        picoscope.close()

        return 'Picoscope disconnected'


configure_routes(app)

if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0")

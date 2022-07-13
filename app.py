"""Flask app connecting pithy container to picoscope container"""

import flask
import json
import logging

logging.basicConfig(filename='logs/logs.log',
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')


def configure_routes(app):
    from picoscope import picoscope

    #test to see that server is alive
    @app.route('/')
    def hello_world():
        return "Flask picoscope server running"


    # Connect to picoscope
    # Keeping it here because the wrapper connection
    # tends to fail a couple of times
    @app.route('/connect')
    def connect():
        picoscope.connect()

        return "Picoscope connected"

    # Runs resonance
    @app.route('/get_resonance', methods=['POST'])
    def get_resonance():
        params_dict_w_strs = flask.request.values.to_dict()
        params = dict([key, float(val)] for key, val in params_dict_w_strs.items())

        data = picoscope.sweep(params=params)

        return json.dumps(data)

    @app.route('/disconnect')
    def disconnect():
        """Mainly for testing purposes. Disconnects the oscilloscope."""
        picoscope.close()

        return 'Picoscope disconnected'


PORT = '5001'

app = flask.Flask(__name__)

configure_routes(app)

if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0")

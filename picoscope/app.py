"""Flask app connecting pithy container to picoscope container"""

import flask
import json

import picoscope

PORT = '5001'

app = flask.Flask(__name__)

#start up the picoscope connection
# Initializing class without connecting to picoscope
picoscope_ = picoscope.Picoscope()

#test to see that server is alive
@app.route('/')
def hello_world():
    return "Flask picoscope server running"

# Connect to picoscope
# Keeping it here because the wrapper connection
# tends to fail a couple of times
@app.route('/connect')
def connect():
    picoscope_.connect()

    return "Picoscope connected"

# Runs resonance
@app.route('/get_resonance', methods=['POST'])
def get_resonance():
    params = flask.request.values.to_dict()    
    data = picoscope_.sweep(params=params)

    return json.dumps(data)
    
if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0")


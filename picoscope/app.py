import flask
import json

import picoscope

PORT = '5001'

app = flask.Flask("pico")

#start up the picoscope connection
# Initializing class without connecting to picoscope
ps = picoscope.Picoscope()

#test to see that server is alive
@app.route('/')
def hello_world():
    return "Flask Picoscope server: running"

# Connect to picoscope
# Keeping it here because the wrapper connection
# tends to fail a couple of times
@app.route('/connect')
def connect():
    ps.connect()

    return "Picoscope connected"

# Runs resonance
@app.route('/get_resonance', methods=['POST'])
def get_resonance():
    params = flask.request.values    
    data = ps.sweep(params=params)

    return json.dumps(data)
    

app.run(port=PORT,host="0.0.0.0")


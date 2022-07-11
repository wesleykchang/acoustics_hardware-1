import flask
import json

import picoscope

PORT = '5001'

# # pythonic function for poking the /test url
# def test(url='http://localhost'):
#     data = requests.get(url+':'+port+'/test')
#     return json.loads(data.text)

if __name__ == "__main__":
    #start up the picoscope connection
    app = flask.Flask("pico")
    ps = picoscope.Picoscope()
    ps.connect()
    
    #test to see that server is alive
    @app.route('/')
    def hello_world():
        return "Welcome to the Picoscope"

    # Runs resonance
    @app.route('/get_resonance', methods=['POST'])
    def get_resonance():
        params = flask.request.values    
        data = ps.sweep(params=params)

        return json.dumps(data)
        

    app.run(port=PORT,host="0.0.0.0")


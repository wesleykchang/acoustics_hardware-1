import sys
import libPicoscope as lps
import flask
import json
import numpy as np
import base64
import requests

port = '5001'

def get_wave(delay, duration, voltage):
        data = requests.post('http://localhost:'+port+'/get_wave',
                             data={'delay':delay, 'duration':duration, 'voltage':voltage})
        return json.loads(data.text)

def test():
        data = requests.get('http://localhost:'+port+'/test')
        return json.loads(data.text)

if __name__ == "__main__":
        app = flask.Flask("pico")
        avg_num = 32
        ps = lps.Picoscope(avg_num = avg_num)
        ps.connect()

        @app.route('/')
        def hello_world():
                return "Welcome to the Picoscope"

        @app.route('/test')
        def getstuff():
                ps.set_maxV(1.0)
                delay = 0.0 #us
                duration = 20.0 #us
                ps.prime_trigger(delay, duration, timeout_ms=1)
                time, data = ps.get_waveform(wait_for_trigger=True)
                return json.dumps(data)

        @app.route('/get_wave', methods=['POST'])
        def getter():
                x = flask.request.values
                delay = float(x['delay'])
                duration = float(x['duration'])
                maxV = float(x['voltage'])
                ps.set_maxV(maxV)
                ps.prime_trigger(delay, duration)
                time, data = ps.get_waveform(wait_for_trigger=True)

                ret_data = {'data':data, 'framerate':ps.sample_rate}
                return json.dumps(ret_data)

        app.run(port=port,host="0.0.0.0")


import sys
import libPicoscope as lps
import flask
import json
import numpy as np
import base64
import requests
import time

if len(sys.argv) > 1:
        port = sys.argv[1]
else:
        port = '5001'

# pythonic function for poking the /get_wave url
def get_wave(delay, duration, voltage='auto', url='http://localhost'):
        data = requests.post(url+':'+port+'/get_wave',
                             data={'delay':delay, 'duration':duration, 'voltage':voltage})
        return json.loads(data.text)

# pythonic function for poking the /test url
def test(url='http://localhost'):
        data = requests.get(url+':'+port+'/test')
        return json.loads(data.text)

if __name__ == "__main__":
        #start up the picoscope connection
        app = flask.Flask("pico")
        avg_num = 32
        ps = lps.Picoscope(avg_num=avg_num)
        ps.connect()
        t = -1  # time of last waveform
        
        #test to see that server is alive
        @app.route('/')
        def hello_world():
                return "Welcome to the Picoscope"

        #test to see that the picoscope is actually talking
        #gives some bs static data
        @app.route('/test')
        def getstuff():
                global t
                ps.set_maxV(1.0)
                delay = 0.0 #us
                duration = 20.0 #us
                ps.prime_trigger(delay, duration, timeout_ms=1)
                time, data = ps.get_waveform()
                t = int(time.time()*1000)
                return json.dumps(data)

        
        #returns the unix time in ms of the last read time
        @app.route('/lastread')
        def lastread():
                return str(t)
        
        #function that actually grabs a wave from the pico
        #PULSER MUST BE RUNNING AT A DECENT RATE (>50 pulses/sec) FOR THIS
        @app.route('/get_wave', methods=['POST'])
        def getter():
                global t
                x = flask.request.values
                delay = float(x['delay'])
                duration = float(x['duration'])
                if 'voltage' in x:
                        maxV = x['voltage']
                        if 'auto' in maxV:
                                ps.auto_range(delay, duration)
                        else:
                                maxV = float(maxV)
                                ps.set_maxV(maxV)
                else:
                        ps.auto_range(delay, duration)
                        
                ps.prime_trigger(delay, duration)
                time, data = ps.get_waveform()

                ret_data = {'data':data, 'framerate':ps.sample_rate}
                t = int(time.time()*1000)
                return json.dumps(ret_data)

        app.run(port=port,host="0.0.0.0")


import sys
sys.path.append('lib') #tells python where to look for packages
from daemon import Daemon
import libacoustic as A
import time
import argparse
from http.server import SimpleHTTPRequestHandler
import socketserver
import json
import utils
import os

from flask import Flask, send_from_directory, request

__all__ = ["AcousticDaemon"]
app = Flask(__name__)


class AcousticDaemon(Daemon):
    def __init__(self,uiurl=5000,muxurl=9002,pulserurl=9003):
        Daemon.__init__(self,self.run,name="easi_daemon")
        self.uiurl =  utils.parse_URL(uiurl)
        self.muxurl =  utils.parse_URL(muxurl)
        self.pulserurl =  utils.parse_URL(pulserurl)
        self.acous = A.Acoustics(json_url= self.uiurl,pulserurl=self.pulserurl,muxurl=self.muxurl,muxtype="cytec")

    def run(self):
        while True:
            self.acous.beginRun()

    def handler(self,fn): #need to reimplement this. right now it's stdin and stdout.
        try:
            fn()
        except:
            pass 

    def loadTools(self):
        pass


class UIDaemon(Daemon):
    """Hosts an editable table at http://localhost:5000"""
    def __init__(self,port=5000,host=None):
        Daemon.__init__(self,self.run,name="ui_daemon")
        self.port = port
        self.host = host

    def run(self):
        @app.route('/')
        def root():
            return send_from_directory('static','index.html')

        @app.route('/table_load')
        def table_load():
            return open("table_state.json").read()

        @app.route('/fonts/<path:filename>') #important for being able to load font files
        def custom_static(filename):
            return send_from_directory("fonts", filename)

        @app.route('/<startdate>/view')
        def view_table(startdate):
            # show the user profile for that user
            return send_from_directory('static/tableviewer','index.html')

        @app.route('/<startdate>/table_load')
        def log_load(startdate):
            return open(os.path.join("Data",startdate,"logfile.json")).read()

        @app.route('/table_save', methods=['GET', 'POST'])
        def table_save():
            # if request.method == 'POST':
                out = {}
                try:
                    test = request.get_data().decode('utf-8')
                    open("table_state.json",'w').write(test)
                    # open("table_state_%i.json" % int(time.time()),'w').write(test)
                    out = json.loads(test)
                    out['status'] = 'success!'
                except Exception as E: 
                    out['status'] = str(E)
                return json.dumps(out)
                
        while True:  
            app.run(host=host,port=port) #if you call this with debug=true, daemon will init twice. weird.

    def loadTools(self):
        pass


if __name__=="__main__":
    pulserurl = 9001
    muxurl = 9000
    host = None
    port = 5000
    for i in sys.argv:
        if i.find("=") > 0: 
            print(i)
            exec(i)
            
    d = UIDaemon(port,host)
    d.start()
    time.sleep(1)
    ad = AcousticDaemon(uiurl=port,muxurl=muxurl,pulserurl=pulserurl)
    ad.start()
